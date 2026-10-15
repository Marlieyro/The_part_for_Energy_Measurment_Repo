import asyncio
import logging
from pymodbus.server import ModbusSerialServer
from pymodbus.simulator import DataType, SimData, SimDevice

# Налаштування логування для відстеження запитів від ESP32
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

async def update_voltage_task(server):
    """Фонова задача для симуляції зміни напруги"""
    voltage = 220
    
    # Даємо серверу 1 секунду на повноцінний запуск перед тим як писати дані
    await asyncio.sleep(1) 
    
    while True:
        try:
            # У новій версії ми оновлюємо дані напряму через об'єкт сервера.
            # device_id=1 (MODBUS_SLAVE_1)
            # func_code=4 (MB_PARAM_INPUT)
            # address=1 (modbus_voltage_register = 0x1)
            await server.async_setValues(
                device_id=1, 
                func_code=4, 
                address=1, 
                values=[voltage]
            )
            log.info(f"Значення напруги оновлено до {voltage} V")
        except Exception as e:
            log.error(f"Помилка оновлення регістра: {e}")
        
        voltage += 1
        if voltage > 240:
            voltage = 220
            
        await asyncio.sleep(2) # Змінюємо значення кожні 2 секунди

async def run_slave():
    # 1. Описуємо блок пам'яті. DataType.REGISTERS підходить для FC3 та FC4
    # address=1 збігається з вашою прошивкою, резервуємо 10 регістрів (count=10)
    sim_data = SimData(address=1, count=10, datatype=DataType.REGISTERS, values=[0]*10)
    
    # 2. Створюємо пристрій з ID = 1 (Slave 1) та прив'язуємо до нього нашу пам'ять
    device = SimDevice(id=1, simdata=[sim_data])
    
    log.info("Запуск Modbus RTU Slave сервера на порту /dev/ttyUSB0...")
    
    # 3. Ініціалізуємо сервер (framer за замовчуванням вже встановлено як RTU)
    server = ModbusSerialServer(
        context=device,
        port='/dev/ttyUSB0',  
        baudrate=115200,
        bytesize=8,
        parity='N',
        stopbits=1
    )

    # 4. Запускаємо фонову задачу, передаючи їй об'єкт сервера
    asyncio.create_task(update_voltage_task(server))
    
    # 5. Запускаємо сервер (ця функція блокує подальше виконання, доки ви не зупините скрипт)
    await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(run_slave())
    except KeyboardInterrupt:
        log.info("Сервер зупинено користувачем.")
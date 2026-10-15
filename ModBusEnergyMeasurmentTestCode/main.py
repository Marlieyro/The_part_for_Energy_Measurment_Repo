import asyncio
#from pymodbus.server import StartSerialServer
from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.framer import ModbusRtuFramer

async def update_voltage_task(context):
    voltage = 220
    while True:
        # fx=4 відповідає за Input Registers (MB_PARAM_INPUT в ESP32)
        # address=1 відповідає modbus_voltage_register = 0x1
        context[1].setValues(4, 1, [voltage])
        #log.info(f"Значення напруги оновлено до {voltage} V")
        
        voltage += 1
        if voltage > 240:
            voltage = 220
            
        await asyncio.sleep(2.0) 

async def run_slave():
    # Input registr only
    store = ModbusSlaveContext(ir=ModbusSequentialDataBlock(1, [0]*10))

    context = ModbusServerContext(slaves={1: store}, single=False)

    asyncio.create_task(update_voltage_task(context))

    print("Modbus Config Done")
    await StartAsyncSerialServer(
        context=context,
        framer=ModbusRtuFramer,
        port='/dev/ttyUSB0',  
        baudrate=115200,
        bytesize=8,
        parity='N',
        stopbits=1
    )
    
if __name__ == "__main__":
    asyncio.run(run_slave())
import psutil
import pynvml
import serial
import time
from serial.tools import list_ports
from abc import ABC, abstractmethod

DEFAULT_DELAY = 250e-3


def byte_to_gb(byte):
    return round(byte / (2**30), 2)


class Component(ABC):
    @abstractmethod
    def percentage_usage(self):
        pass

    @abstractmethod
    def limit(self):
        pass

    @abstractmethod
    def current(self):
        pass


class RAM(Component):
    def __init__(self):
        self.intalled_memory = psutil.virtual_memory().total

    def percentage_usage(self):
        return round(psutil.virtual_memory().percent)

    def limit(self):
        return byte_to_gb(self.intalled_memory)

    def current(self):
        return byte_to_gb(psutil.virtual_memory().used)


class CPU(Component):
    def __init__(self):
        self.max_cpu_freq = psutil.cpu_freq().max

    def percentage_usage(self):
        return round(psutil.cpu_percent())

    def limit(self):
        return self.max_cpu_freq

    def current(self):
        return psutil.cpu_freq().current


class GPU(Component):
    def __init__(self):
        pynvml.nvmlInit()
        self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
        self.installed_gpu_memory = memory_info.total

    def percentage_usage(self):
        utilization = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
        gpu_usage = utilization.gpu
        return round(gpu_usage)

    def current(self):
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
        return byte_to_gb(memory_info.used)

    def limit(self):
        return byte_to_gb(self.installed_gpu_memory)

    def __del__(self):
        pynvml.nvmlShutdown()


def get_arduino(serial_number="5563931383235150A122"):
    com_ports = list_ports.comports()

    for device in com_ports:
        if device.serial_number == serial_number:
            arduino = serial.Serial(device.device, 9600)
    return arduino


def format_arduino_message(cpu_usage, gpu_usage, ram_usage, vram_usage):
    cpu_usage = min(max(cpu_usage, 0), 99)
    gpu_usage = min(max(gpu_usage, 0), 99)
    return f"{cpu_usage},{gpu_usage},{round(ram_usage, 1)},{round(vram_usage, 1)};"


if __name__ == "__main__":
    cpu = CPU()
    gpu = GPU()
    ram = RAM()
    arduino = get_arduino()

    while True:
        message = format_arduino_message(
            cpu.percentage_usage(), gpu.percentage_usage(), ram.current(), gpu.current()
        )
        print(f"Sending to Arduino: {message}")
        arduino.write(message.encode())
        time.sleep(DEFAULT_DELAY)

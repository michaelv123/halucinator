from .arm_qemu import ARMQemuTarget
from .. import hal_log
hal_log = hal_log.getHalLogger()

class ARMv7mQemuTarget(ARMQemuTarget):

    def trigger_interrupt(self, interrupt_number, cpu_number=0):
        hal_log.info("Injecting interrupt %d" % interrupt_number)
        self.protocols.monitor.execute_command(
            'avatar-armv7m-inject-irq',
            {'num_irq': interrupt_number, 'num_cpu': cpu_number})

    def set_vector_table_base(self, base, cpu_number=0):
        hal_log.info("Setting vector table base to 0x%x" % base)
        self.protocols.monitor.execute_command(
            'avatar-armv7m-set-vector-table-base',
            {'base': base, 'num_cpu': cpu_number})

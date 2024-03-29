from migen import *

from migen.genlib.io import CRG

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

import litex.soc.integration.soc_core as SC
from litex.soc.integration.builder import *

from ios import Led
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores import gpio

from i2s import I2S

#
# platform
#
# vcc
# gnd   GND
# cs    P26
# rst   P29  gpio0
# dc    P30  gpio1
# mosi  P33
# sck   P35
# led   P59  gpio2
# miso  P79

_io = [


    ("user_led",  0, Pins("T8"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("V9"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("R8"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("T6"), IOStandard("LVCMOS33")),
    ("user_led",  4, Pins("T5"), IOStandard("LVCMOS33")),
    ("user_led",  5, Pins("T4"), IOStandard("LVCMOS33")),
    ("user_led",  6, Pins("U7"), IOStandard("LVCMOS33")),
    ("user_led",  7, Pins("U6"), IOStandard("LVCMOS33")),
    ("user_led",  8, Pins("V4"), IOStandard("LVCMOS33")),


    ("clk32", 0, Pins("E3"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("D4")),
        Subsignal("rx", Pins("C4")),
        IOStandard("LVCMOS33"),
    ),


    ("spi_master", 0, ### JC
    	Subsignal("cs_n", Pins("K2")),
        Subsignal("clk", Pins("E7")),
        Subsignal("mosi", Pins("J3")),
        Subsignal("miso", Pins("J4")),
        IOStandard("LVCMOS33")
    ),
    ###JC
    ("control_lcd",0,Pins("K1"), IOStandard("LVCMOS33")),##ctrl reset
    ("control_lcd",1,Pins("E6"), IOStandard("LVCMOS33")),##ctrl dc
    ("control_lcd",2,Pins("J2"), IOStandard("LVCMOS33")),##ctrl led


    ("i2s_", 0,        ###JA
        Subsignal("bclk_", Pins("B13")),
        Subsignal("din_", Pins("F14")),
        Subsignal("ws_", Pins("D17")),
        IOStandard("LVCMOS33")
    ),

]


class Platform(XilinxPlatform):
    default_clk_name = "clk32"
    default_clk_period = 10

    def __init__(self):
#        XilinxPlatform.__init__(self, "xc6slx9-TQG144-2", _io, toolchain="ise")
        XilinxPlatform.__init__(self, "xc7a100t-CSG324-1", _io, toolchain="ise")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment, ngdbuild_opt="ngdbuild -p")


#
# design
#

# create our platform (fpga interface)
platform = Platform()

# create our soc (fpga description)
class BaseSoC(SC.SoCCore):
    # Peripherals CSR declaration
    csr_peripherals = {
      "leds": 2,
      "spi": 3,
      "ctrllcd" :4,
      "i2s": 5
    }
    SC.SoCCore.csr_map= csr_peripherals

    def __init__(self, platform):
        sys_clk_freq = int(100e6)
        # SoC with CPU
        SC.SoCCore.__init__(self, platform,
            cpu_type="lm32",
            clk_freq=100e6,
            ident="CPU Test SoC", ident_version=True,
            integrated_rom_size=0x8000,
            csr_data_width=32,
            integrated_main_ram_size=16*1024)

        # Clock Reset Generation
        self.submodules.crg = CRG(platform.request("clk32"), ~platform.request("cpu_reset"))

 	      # Led
        user_leds = Cat(*[platform.request("user_led", i) for i in range(9)])
        self.submodules.leds = Led(user_leds)
	       # Spi
        self.submodules.spi = SPIMaster(platform.request("spi_master"))
        # control_lcd
        control_lcd = Cat(*[platform.request("control_lcd", i) for i in range(3)])
        self.submodules.ctrllcd = gpio.GPIOOut(control_lcd)

        self.submodules.i2s = I2S(platform.request("i2s_"))

soc = BaseSoC(platform)


#
# build
#

builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.build()

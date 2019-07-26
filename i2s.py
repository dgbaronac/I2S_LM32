from migen import *
from migen.genlib.fsm import *
from migen.fhdl import verilog
from litex.soc.interconnect.csr import*

class _divisor(Module):
    def __init__(self,freq_in, freq_out): ###declaracion de las variables, frecuencia maxima 44k
        self.counter=Signal(32)
        self.divisor =Signal(1)
        self.sync += [
            self.counter.eq(self.counter+1),
            If(self.counter == int((freq_in//freq_out)-1),
                self.counter.eq(0),
                self.divisor.eq(~self.divisor)
            )

        ]


#class _i2s(Module,AutoCSR):
#    def __init__(self):
#        self.data = Signal(32)
#        self.busy = Signal()
#        self.init = Signal()

#        self.bclk = Signal()
#        self.din = Signal()
#        self.ws = Signal()


#        self.sync += [


#        ]

#        self.comb += [

#        ]


class I2S(Module, AutoCSR):
    def __init__(self, pads, clk_freq=100000000):
        self.data=CSRStatus(32)
        self.busy=CSRStatus()
        self.init=CSRStatus()
        self.bclk = pads.bclk_
        self.din = pads.din_
        self.ws = pads.ws_

        self.div=0
        self.div = _divisor(clk_freq, 44100)  ###llamar a la funcion _divisor
        ###
        self.bclk.eq(self.div.divisor)
        self.tx_bitno = tx_bitno = Signal(5)  ###32 bits tx
        self.tx_latch = tx_latch = Signal(32)   ###Tamano de palabra

        self.submodules.tx_fsm = FSM(reset_state="IDLE")  ###IDLE es un estado libre
        self.tx_fsm.act("IDLE",
            If(self.init.status,
                NextValue(tx_latch, self.data.status), ###prepara tamano de palabra y los datos
                NextValue(tx_bitno, 0),
                NextState("START")
            ).Else(
                NextValue(self.busy.status, 0)
            )
        )
        self.tx_fsm.act("START",   ### inicia busy y el envio de datos
            NextValue(self.busy.status, 1),
            NextState("DATA")
        )
        self.tx_fsm.act("DATA",
            NextValue(self.din  , tx_latch[31]),
            NextValue(tx_latch, Cat(0, tx_latch[0:30])),
            NextValue(tx_bitno, tx_bitno + 1),
            If(self.tx_bitno == 32,
                    NextState("STOP")  ### cuenta el bit hasta ser 32 y detenerse
            )

        )
        self.tx_fsm.act("STOP",
            NextValue(self.din, 1),
            NextValue(self.busy.status, 0),
            NextState("IDLE")   ###nuevamente en estado "libre"

        )




#print(verilog.convert( I2S()))

"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."
        
        # Initialize topology
        Topo.__init__( self )
        
        # Add hosts and switches
        emissor1 = self.addHost( 'h1' )
        exibidor1000 = self.addHost( 'h2' )
	servidor = self.addHost( 'h3' )
	emissor2 = self.addHost( 'h4' )
        exibidor1001 = self.addHost( 'h5' )

        switch1 = self.addSwitch( 's1' )
	switch2 = self.addSwitch( 's2' )
	switch3 = self.addSwitch( 's3' )
	switch4 = self.addSwitch( 's4' )
        
        # Add links
        self.addLink(emissor1, switch1)
        self.addLink(exibidor1000, switch1)
        self.addLink(switch1, switch4)
        self.addLink(switch4, switch2)
        self.addLink(switch2, servidor)
        self.addLink(switch4, switch3)
        self.addLink(switch3, emissor2)
        self.addLink(exibidor1001, switch3)


topos = { 'mytopo': ( lambda: MyTopo() ) }

from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        leftSwitch = self.addSwitch( 's1' )
        rightSwitch = self.addSwitch( 's2' )

        # Add links
        self.addLink( leftHost, leftSwitch, cls=TCLink, bw=15)
        self.addLink( rightHost, rightSwitch, cls=TCLink, bw=15)
        self.addLink( rightSwitch, leftSwitch, cls=TCLink, bw=15)


topos = { 'mytopo': ( lambda: MyTopo() ) }

from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftLeftHost = self.addHost( 'h1' )
        leftRightHost = self.addHost( 'h2' )
        rightLeftHost = self.addHost( 'h3' )
        rightRightHost = self.addHost( 'h4' )
        leftSwitch = self.addSwitch( 's1' )
        rightSwitch = self.addSwitch( 's2' )

        # Add links
        self.addLink( leftLeftHost, leftSwitch, cls=TCLink, delay='20ms')
        self.addLink( leftRightHost, leftSwitch, cls=TCLink, delay='20ms')
        self.addLink( rightLeftHost, rightSwitch, cls=TCLink, delay='15ms')
        self.addLink( rightRightHost, rightSwitch, cls=TCLink, delay='1s')
        self.addLink( rightSwitch, leftSwitch, cls=TCLink, delay='50ms')


topos = { 'mytopo': ( lambda: MyTopo() ) }

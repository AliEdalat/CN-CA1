from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )
        thirdHost = self.addHost( 'h3' )
        forthHost = self.addHost( 'h4' )
        switch = self.addSwitch( 's1' )

        # Add links
        self.addLink( firstHost, switch, cls=TCLink, bw=15, max_queue_size=1000)
        self.addLink( secondHost, switch, cls=TCLink, bw=15, max_queue_size=1000)
        self.addLink( thirdHost, switch, cls=TCLink, bw=15, max_queue_size=1000)
        self.addLink( forthHost, switch, cls=TCLink, bw=15, max_queue_size=1000)


topos = { 'mytopo': ( lambda: MyTopo() ) }

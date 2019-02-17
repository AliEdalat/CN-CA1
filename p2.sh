# Create host namespaces
ip netns add h1
ip netns add h2
ip netns add h3

# Create switch
ovs-vsctl add-br s1
ovs-vsctl add-br s2

# Create links
ip link add h1-eth0 type veth peer name s1-eth1
ip link add h2-eth0 type veth peer name s1-eth2
ip link add s2-eth1 type veth peer name s1-eth3
ip link add h3-eth0 type veth peer name s2-eth2
ip link show

# Move host ports into namespaces
ip link set h1-eth0 netns h1
ip link set h2-eth0 netns h2
ip link set h3-eth0 netns h3

# Connect switch ports to OVS
ovs-vsctl add-port s1 s1-eth1
ovs-vsctl add-port s1 s1-eth2
ovs-vsctl add-port s1 s1-eth3
ovs-vsctl add-port s2 s2-eth1
ovs-vsctl add-port s2 s2-eth2
ovs-vsctl show

# Configure network
ip netns exec h1 ifconfig h1-eth0 10.1
ip netns exec h1 ifconfig lo up
ip netns exec h2 ifconfig h2-eth0 10.2
ip netns exec h2 ifconfig lo up
ip netns exec h3 ifconfig h3-eth0 10.3
ip netns exec h3 ifconfig lo up
ifconfig s1-eth1 up
ifconfig s1-eth2 up
ifconfig s1-eth3 up
ifconfig s2-eth1 up
ifconfig s2-eth2 up

# Test network
ip netns exec h1 ping -c1 10.3

import socket

def elect_leader(udp_port=6666):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        sock.bind(('', udp_port))
        print("Elected as Leader")
        # Keep the socket open and add a mechanism to ensure it's not closed inadvertently
        global leader_socket
        leader_socket = sock
        return True
    except socket.error as e:
        print("Operating as Follower", str(e))
        return False

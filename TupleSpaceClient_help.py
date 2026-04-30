import socket
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    try:
        sock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((hostname,port))
    except socket.error as e:
        print(f"Error connecting to server : {e}")
        sys.exit(1)
    
    
    
    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            if len(parts) < 2:
                print(f"Error: Invalid line format : {line}")
                continue
            cmd = parts[0]
            key=parts[1]
            value=parts[2] if len(parts)>2 else""
            
            #verify opreation type
            if cmd not in ["READ","GET","PUT"]:
                print(f"Error:Unknown command '{cmd}' in line:{line}")
                continue
            
            
            #verify len key
            if len (key)>999:
                print(f"Error:Value for key '{key}' exceeds 999 characters")
                continue
            
            
            if len (key) + 1 + len (value) > 970:
                print(f"Error : key + value size exceeds 970 characters for line :{line}")
                continue
            
            

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            
            if cmd == "READ":
                op_code ="R"
                total_size = 6 + len(key)
                message =f"{total_size :03d} {op_code} {key}"
            elif cmd=="GET":
                op_code ="G"
                total_size = 6+len(key)
                message= f"{total_size :03d} {op_code} {key}"
            else:
                op_code = "P"
                total_size= 7 + len(key) +len(value)
                message= f"{total_size :03d} {op_code} {key} {value}"
                
            #verify message length again 
            if total_size > 999:
                print(f"Error : Message size {total_size} exceeds maximum 999 for line :{line}")
                continue
            
            


            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.
            try:
                sock.sendall(message.encode())
                
                size_bytes = sock.recv(3)
                if len(size_bytes) < 3:
                    print(f"Error: Failed to receive response size for: {line}")
                    continue
                
                try:
                    response_size = int(size_bytes.decode())
                except ValueError:
                    print(f"Error: Invalid response size for: {line}")
                    continue
        
                remaining_bytes = response_size - 3
                if remaining_bytes > 0:
                    response_body = sock.recv(remaining_bytes)
                    if len(response_body) < remaining_bytes:
                        print(f"Error: Incomplete response for: {line}")
                        continue
                else:
                    response_body = b""
                
                response_buffer = size_bytes + response_body
                response = response_buffer.decode().strip()
                print(f"{line}: {response}")
                
            except (socket.error, ValueError) as e:
                print(f"Error processing line '{line}': {e}")
                continue

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
           
    
        # TASK 4: Close the socket when done (already called for you — explain why
        # finally: is the right place to do this even if an error occurs above).
        sock.close()

if __name__ == "__main__":
    main()
# coding=utf-8
"""
    DNS Module
"""
import socket
import struct


class DNSLookUp(object):
    """
        DNS Class
    """

    def __init__(self, dns_server_ip, domain_name, port=53):
        """
        Constructor
        :type dns_server_ip: str
        :type domain_name: str
        :type port: int
        """
        self._dns_server_ip = dns_server_ip
        self._domain_name = domain_name
        self._port = port

        self._type = None
        self._query = None
        self._dns_message = None
        self._socket_connection = None
        self._question = ""

        self.__l1 = "\x41\x41"
        self.__l2 = "\x01\x00"
        self.__l3 = "\x00\x01"
        self.__l4 = "\x00\x00"
        self.__l5 = "\x00\x00"
        self.__l6 = "\x00\x00"

        self._dns_reply = {}

        self.__header = self.__l1 + self.__l2 + self.__l3 + self.__l4 + self.__l5 + self.__l6

    @property
    def dns_reply(self):
        """
        Get DNS reply
        :return: 
        """
        return self._dns_reply

    def create_dns_message(self):
        """
        Make a dns_message and then send the dns message to DNS server using UDP
        :return: 
        """
        self._question = ""

        if self._domain_name != "":
            for item in self._domain_name.split('.'):
                self._question = self._question + struct.pack("!b{}s".format(str(len(item))), len(item), item)

            self._query = self._question + "\x00\x00\x01\x00\x01"
            self._dns_message = self.__header + self._query

            return self._dns_message
        else:
            raise Exception("No domain name provided !")

    def dns_look_up(self, dns_message):
        """
        Interrogate the DNS Server
        :type dns_message: str | byte
        :return: 
        """
        # noinspection PyArgumentEqualDefault
        self._socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_server = (self._dns_server_ip, self._port)
        data = None

        try:
            self._socket_connection.settimeout(5)
            self._socket_connection.sendto(dns_message, dns_server)
            data, address = self._socket_connection.recvfrom(1024)
        except Exception as exc:
            print("No response from server {}:\nError: {}".format(dns_server, exc))
            self._socket_connection.close()

        # get the message from the server
        server_message = data.split(',', 0)
        reply = str(server_message[0].encode('hex'))

        response_code = reply[:8]
        response_code = response_code[7:]

        r_code = int(response_code)

        # check the r_code with error detection
        # if there is no error, then get the ip address
        if r_code == 0:
            # check the ANCOUNT to find the number of answers
            answer_count = reply[:16]
            answer_count = answer_count[12:]
            nb_of_answers = int(answer_count)

            # get the answer from the server reply
            answer = reply[2 * len(dns_message):]

            for idx in range(0, nb_of_answers):

                _key = "answer_{}".format(idx + 1)
                self._dns_reply[_key] = {}

                answer = answer[4:]

                # get the TYPE from the answer
                _type = answer[:4]
                if _type == "0001":
                    self._dns_reply[_key]["TYPE"] = "A"

                elif _type == "0005":
                    self._dns_reply[_key]["TYPE"] = "CNAME"

                else:
                    self._dns_reply[_key]["TYPE"] = _type

                answer = answer[4:]

                # get the CLASS from the answer
                _class = answer[:4]
                if _class == "0001":
                    self._dns_reply[_key]["CLASS"] = "IN"

                else:
                    self._dns_reply[_key]["CLASS"] = _class

                answer = answer[4:]

                # get the TTL from the answer
                ttl = answer[:8]
                self._dns_reply[_key]['TTL'] = int(ttl, 16)

                answer = answer[8:]

                # get the RDLENGTH from the answer
                rd_lenght = answer[:4]
                self._dns_reply[_key]['RDLENGTH'] = int(rd_lenght, 16)
                answer = answer[4:]

                # get the RDATA from the answer
                r_data = answer[:int(rd_lenght, 16) * 2]
                answer = answer[int(rd_lenght, 16) * 2:]

                # get the IP from the RDATA if the TYPE is A
                if _type == "0001":
                    temp = int(r_data, 16)
                    ip4 = temp & 0xff
                    temp = temp >> 8
                    ip3 = temp & 0xff
                    temp = temp >> 8
                    ip2 = temp & 0xff
                    temp = temp >> 8
                    ip1 = temp & 0xff

                    ip = "{}.{}.{}.{}".format(str(ip1), str(ip2), str(ip3), str(ip4))

                    self._dns_reply[_key]['IP'] = ip
                else:  # get the CNAME from the RDATA if the TYPE is CNAME
                    cname = ""
                    r_data = r_data[2:]
                    # print the CNAME
                    for j in range(int(rd_lenght, 16) - 3):

                        n = r_data[:2]
                        n = int(n, 16)
                        r_data = r_data[2:]
                        if n <= 32:
                            cname += "."
                        cname = cname + chr(n)

                    self._dns_reply[_key]['CNAME'] = cname

        elif r_code == 1:
            raise Exception("Format error: the name server was unable to interpret the query.")

        elif r_code == 2:
            raise Exception("Server failure: the name server was unable to process this query due to a problem with the name server.")

        elif r_code == 3:
            raise Exception("None exist domains: server can not find answer.")

        elif r_code == 4:
            raise Exception("Not Implemented: the name server does not support the requested kind of query.")

        elif r_code == 5:
            raise Exception("Server Refused.")

        else:
            raise Exception("Other errors")


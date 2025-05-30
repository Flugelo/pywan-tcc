import ipaddress
import json
import re
import os
import sys

class Tools():
    #Verifica se um endereço IP é privado ou público.
    def is_private_ip(self, ip: str) -> bool:
        try:
            ip_address = ipaddress.ip_address(ip)
            return ip_address.is_private
        except ValueError:
            # Se o endereço IP não puder ser analisado, é considerado inválido e público.
            return False


    #Recupera as configurações do arquivo config.json
    def read_configuration(self, nome_arquivo) -> any:
        if os.path.exists('config.json'):
            with open(nome_arquivo, "r") as arquivo:
                configuracao = json.load(arquivo)
            return configuracao
        else:
            print('[ERROR] - Arquivo de configuração (config.json) não encontrado.')



    # Extrair o valor do ping do comando da Routerboard Mikrotik.
    #Checa se a requesição obteve um status diferente de OK
    def extract_ping_time(self, result):

        if 'status' in result[0]:
                return result[0]['status']

        time_str = result[0]['time']
        time_ms = re.findall(r'\d+', time_str)[0]
        return int(time_ms)

    def get_ms(self, obj):
        ms = obj["latency"]
        if isinstance(ms, str):
            if ms.isdigit():
                return float(ms)
            else:
                return float("inf")
        else:
            return ms

    def insert_address_in_list(self, results: [], operadoras: [], debug: bool) -> []:

        for result in results:

            src_address = result['address']
            list_name = result['list']

            for operadora in operadoras:
                if operadora['list_name'] == list_name:
                    operadora['addresses'].append(src_address)

                    if debug : print('[DEBUG] - O endereço ' + src_address + ' foi adicionada à lista ' + list_name + '.')

        return operadoras

    def get_best_latency(self, latency_test : [],index, total, debug):
        best_operator = sorted(latency_test, key=self.get_ms)[0]

        return best_operator

    def get_block_ip(self, address, mask):
        try:
            if self.if_ip_address(address):
                # Cria um objeto de rede com o IP e a máscara de sub-rede
                rede = ipaddress.IPv4Network(f"{address}/{mask}", strict=False)
                return rede
        except ValueError as e:
            print(f"Erro ao criar objeto de rede: {e}")
            sys.exit()

    def clear_address_with_mask(self, address):            
        ip = ipaddress.ip_address(ip)
        for block in blacklist:
            network = ipaddress.ip_network(block)
            if ip in network:
                return True  # O IP está na blacklist
        return False  # O IP não está na blacklistato_personalizado)

    def if_ip_address(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def inside_block_address(self, block, address):
        try:
            endereco_ip = ipaddress.ip_address(address)
            rede = ipaddress.ip_network(block, strict=False)
            return endereco_ip in rede

        except ValueError as e:
            return False
        
    def is_valid_ip(self, ip: str) -> bool:
        try:
            # Tenta criar um objeto IP. Se falhar, o IP é inválido.
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
        
    def is_ip_in_blacklist(self, ip, blacklist):
        """
        Verifica se um endereço IP está em uma lista de blocos de IPs (blacklist).
        
        Parâmetros:
        - ip (str): O endereço IP a ser verificado, no formato "x.x.x.x".
        - blacklist (list): Lista de blocos de IPs em formato CIDR, por exemplo, ["200.129.130.128/26", "131.0.119.224/27"].
        
        Retorna:
        - bool: True se o IP estiver em algum dos blocos na blacklist, False caso contrário.
        """
        # Converte o IP para o tipo ipaddress.IPv4Address
        ip_obj = ipaddress.ip_address(ip)
        
        # Itera sobre cada bloco na blacklist
        for cidr_block in blacklist:
            try:
                # Converte o bloco CIDR para o tipo ipaddress.IPv4Network, desativando o modo estrito
                network = ipaddress.ip_network(cidr_block, strict=False)
                
                # Verifica se o IP está no bloco de rede
                if ip_obj in network:
                    return True  # IP está na blacklist
            except ValueError as e:
                print(f"Erro ao processar o bloco {cidr_block}: {e}")
        
        # IP não está em nenhum dos blocos
        return False

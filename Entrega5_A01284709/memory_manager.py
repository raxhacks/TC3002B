class MemoryManager:
    def __init__(self):
        self.address_ranges = {
            'global_int': (1000, 1999),
            'global_float': (2000, 2999),
            'local_int': (3000, 3999),
            'local_float': (4000, 4999),
            'temp_int': (5000, 5999),
            'temp_float': (6000, 6999),
            'temp_bool': (7000, 7999),
            'const_int': (8000, 8999),
            'const_float': (9000, 9999),
            'param_int': (10000, 10999),
            'param_float': (11000, 11999),
            'return_int': (12000, 12999),
            'return_float': (13000, 13999),
        }

        # inicializamos las direcciones actuales para cada segmento
        self.current_address = {seg: start for seg, (start, end) in self.address_ranges.items()}
        
        # guardamos las direcciones de las variables y constantes
        self.variable_addresses = {}  # {var_name: address}
        self.constants = {
            'int': {},  # {value: address}
            'float': {}
        }
    
    def get_type_from_address(self, address):
        if 1000 <= address < 2000 or 3000 <= address < 4000 or 5000 <= address < 6000 or 8000 <= address < 9000:
            return 'int'
        elif 2000 <= address < 3000 or 4000 <= address < 5000 or 6000 <= address < 7000 or 9000 <= address < 10000:
            return 'float'
        elif 7000 <= address < 8000:
            return 'bool'
        else:
            raise ValueError(f"Invalid address: {address}")
        
    def allocate_global(self, var_name, var_type):
        segment = f"global_{var_type}"
        return self._allocate_variable(var_name, segment)

    def allocate_local(self, var_name, var_type):
        segment = f"local_{var_type}"
        return self._allocate_variable(var_name, segment)

    def allocate_param(self, param_name, param_type):
        segment = f"local_{param_type}"

        if param_name in self.variable_addresses:
            return self.variable_addresses[param_name]
            
        address = self.current_address[segment]
        
        # checamos si el segmento esta lleno
        if address > self.address_ranges[segment][1]:
            raise MemoryError(f"Out of memory in {segment} segment")
        
        self.current_address[segment] += 1
        self.variable_addresses[param_name] = address
        return address

    def _allocate_variable(self, var_name, segment):
        if var_name in self.variable_addresses:
            return self.variable_addresses[var_name]
            
        address = self.current_address[segment]
        
        # checamos si el segmento esta lleno
        if address > self.address_ranges[segment][1]:
            raise MemoryError(f"Out of memory in {segment} segment")
        
        self.current_address[segment] += 1
        self.variable_addresses[var_name] = address
        return address

    def get_temp_address(self, temp_type):
        segment = f"temp_{temp_type}"
        address = self.current_address[segment]
        
        if address > self.address_ranges[segment][1]:
            raise MemoryError(f"Out of temporary memory in {segment} segment")
        
        self.current_address[segment] += 1
        return address

    def get_constant_address(self, value, const_type):
        if value in self.constants[const_type]:
            return self.constants[const_type][value]
        
        segment = f"const_{const_type}"
        address = self.current_address[segment]
        
        if address > self.address_ranges[segment][1]:
            raise MemoryError(f"Out of memory in {segment} segment")
        
        self.constants[const_type][value] = address
        self.current_address[segment] += 1
        return address

    def get_variable_address(self, var_name):
        if var_name not in self.variable_addresses:
            raise KeyError(f"Variable '{var_name}' not allocated")
        return self.variable_addresses[var_name]

    def reset_local_memory(self):
        self.current_address['local_int'] = 3000
        self.current_address['local_float'] = 4000
        # removemos las variables locales del mapping
        self.variable_addresses = {
            k: v for k, v in self.variable_addresses.items() 
            if v < 3000
        }
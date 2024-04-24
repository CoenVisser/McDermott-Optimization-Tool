class vehicle:
    def __init__(self, fuel_consumption, speed, material, capacity):
        self.material = material 
        self.capacity = capacity # [kg]
        
        # convert fuel consumption from L/h to L/sec
        self.fuel_consumption_Ls = fuel_consumption / 3600

        # convert speed from km/h to m/s
        self.speed_ms = speed / 3.6

        # calculate the fuel consumption (Liter) per meter driven
        self.fuel_consumption_per_meter = self.fuel_consumption_Ls / self.speed_ms
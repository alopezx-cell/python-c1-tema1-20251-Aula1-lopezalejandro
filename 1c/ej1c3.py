"""
Enunciado:
Este ejercicio introduce el uso de clases y programación orientada a objetos (POO)
para modelar y procesar datos de una API pública.

Utilizaremos la API de GBFS (General Bikeshare Feed Specification) del sistema de
bicicletas compartidas de Barcelona para consultar el estado en tiempo real de las estaciones,
modelando los datos obtenidos como objetos Python.

Tareas:
1. Completar la implementación de las clases que representan los diferentes elementos
   del sistema (estación, estado, tipos de bicicletas disponibles)
2. Implementar un cliente que consulte la API y transforme los datos JSON en objetos Python
3. Añadir métodos para analizar la disponibilidad de bicicletas en las estaciones

Esta práctica refuerza conceptos de POO en Python como:
- Uso de enumeraciones (Enum)
- Uso de dataclasses para modelos de datos
- Diseño orientado a objetos
- Transformación de datos JSON a objetos Python
- Manejo de errores y excepciones
"""

import requests
import enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class StationStatus(enum.Enum):
    """
    Enumeración que representa los posibles estados de una estación.
    """
    # Define aquí los estados posibles (IN_SERVICE, MAINTENANCE, etc.)
    # según la documentación de la API
    IN_SERVICE = "IN_SERVICE"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class VehicleType:
    """
    Clase que representa un tipo de vehículo y su cantidad disponible.
    """
    # Añade aquí los atributos necesarios: tipo de vehículo (vehicle_type_id) y cantidad (count)
    vehicle_type_id: str
    count: int


class StationStatusInfo:
    """
    Clase que representa el estado de una estación de bicicletas compartidas.

    Atributos:
        station_id: Identificador único de la estación
        status: Estado actual de la estación (enum StationStatus)
        num_bikes_available: Número total de bicicletas disponibles
        num_bikes_disabled: Número de bicicletas fuera de servicio
        num_docks_available: Número de anclajes disponibles
        is_renting: Indica si la estación permite alquilar bicicletas
        is_returning: Indica si la estación permite devolver bicicletas
        last_reported: Timestamp del último reporte de estado
        vehicle_types: Lista de tipos de vehículos disponibles
    """

    def __init__(self, station_data):
        """
        Inicializa una instancia de StationStatusInfo a partir de los datos
        de la estación proporcionados por la API.

        Args:
            station_data: Diccionario con los datos de la estación obtenidos de la API
        """
        # Implementa aquí la inicialización de todos los atributos
        # a partir del diccionario station_data
        self.station_id = station_data["station_id"]
        self.num_bikes_available = station_data["num_bikes_available"]
        self.num_bikes_disabled = station_data["num_bikes_disabled"]
        self.num_docks_available = station_data["num_docks_available"]
        self.is_renting = station_data["is_renting"]
        self.is_returning = station_data["is_returning"]
        self.last_reported = station_data["last_reported"]
        # convertimos el string al enum
        self.status = StationStatus[station_data["status"]]
        # lista de tipos de vehiculos disponibles
        tipos = station_data.get("vehicle_types_available", [])
        self.vehicle_types = []
        for t in tipos:
          vt = VehicleType(vehicle_type_id=t["vehicle_type_id"], count=t["count"])
          self.vehicle_types.append(vt)

    @property
    def is_operational(self) -> bool:
        """
        Indica si la estación está completamente operativa
        (en servicio y permite alquilar y devolver bicicletas)

        Returns:
            bool: True si la estación está operativa, False en caso contrario
        """
        # Implementa aquí la lógica para determinar si la estación está operativa
        if self.status == StationStatus.IN_SERVICE and self.is_renting and self.is_returning:
          return True
        return False

    def get_available_bikes_by_type(self) -> Dict[str, int]:
        """
        Devuelve un diccionario con la cantidad de bicicletas disponibles por tipo.

        Returns:
            Dict[str, int]: Diccionario donde la clave es el tipo de bicicleta
                            y el valor es la cantidad disponible
        """
        # Implementa aquí la lógica para devolver un diccionario
        # con la cantidad de bicicletas disponibles por tipo
        res = {}
        for vt in self.vehicle_types:
          res[vt.vehicle_type_id] = vt.count
        return res

    def __str__(self) -> str:
        """
        Devuelve una representación en string de la estación con su estado actual.

        Returns:
            str: Representación en texto del estado de la estación
        """
        # Implementa aquí la lógica para devolver una representación en texto
        # de la estación y su estado actual
        return f"Estacion {self.station_id}: {self.num_bikes_available} bikes disponibles, estado: {self.status.name}"


class BarcelonaBikingClient:
    """
    Cliente para consultar el estado de las estaciones de bicicletas de Barcelona.
    """

    def __init__(self):
        """
        Inicializa el cliente con la URL base de la API.
        """
        self.base_url = "https://barcelona.publicbikesystem.net/customer/gbfs/v2/en"
        self.station_status_url = f"{self.base_url}/station_status"

    def get_stations_status(self) -> Tuple[List[StationStatusInfo], Optional[datetime]]:
        """
        Obtiene el estado actual de todas las estaciones de bicicletas.

        Returns:
            Tuple[List[StationStatusInfo], Optional[datetime]]:
                - Lista de objetos StationStatusInfo, uno por cada estación
                - Timestamp de la última actualización de los datos, o None si hay error
        """
        # Implementa aquí la lógica para:
        # 1. Realizar una petición GET a la URL de station_status
        # 2. Verificar que la respuesta sea correcta (código 200)
        # 3. Crear objetos StationStatusInfo para cada estación en la respuesta
        # 4. Extraer el timestamp de last_updated de la respuesta
        # 5. Manejar posibles errores (conexión, formato, etc.)
        try:
          res = requests.get(self.station_status_url)
          if res.status_code != 200:
            return [], None
          datos = res.json()
          estaciones = []
          for s in datos["data"]["stations"]:
            estaciones.append(StationStatusInfo(s))
          last_updated = datos["last_updated"]
          return estaciones, last_updated
        except Exception:
          return [], None

    def find_station_by_id(self, station_id: str) -> Optional[StationStatusInfo]:
        """
        Busca una estación específica por su ID.

        Args:
            station_id: ID de la estación a buscar

        Returns:
            Optional[StationStatusInfo]: Objeto con la información de la estación,
                                         o None si no se encuentra
        """
        # Implementa aquí la lógica para buscar y devolver una estación por su ID
        estaciones, _ = self.get_stations_status()
        for s in estaciones:
          if s.station_id == station_id:
            return s
        return None

    def get_operational_stations(self) -> List[StationStatusInfo]:
        """
        Obtiene la lista de estaciones que están completamente operativas.

        Returns:
            List[StationStatusInfo]: Lista de estaciones operativas
        """
        # Implementa aquí la lógica para filtrar y devolver solo las estaciones operativas
        estaciones, _ = self.get_stations_status()
        operativas = []
        for s in estaciones:
          if s.is_operational:
            operativas.append(s)
        return operativas

    def get_stations_with_available_bikes(self, min_bikes: int = 1) -> List[StationStatusInfo]:
        """
        Obtiene la lista de estaciones que tienen al menos min_bikes disponibles.

        Args:
            min_bikes: Número mínimo de bicicletas requeridas (por defecto 1)

        Returns:
            List[StationStatusInfo]: Lista de estaciones con bicicletas disponibles
        """
        # Implementa aquí la lógica para filtrar y devolver las estaciones
        # con al menos min_bikes disponibles
        estaciones, _ = self.get_stations_status()
        res = []
        for s in estaciones:
          if s.num_bikes_available >= min_bikes:
            res.append(s)
        return res


if __name__ == "__main__":
    # Ejemplo de uso del cliente
    client = BarcelonaBikingClient()

    # Obtener el estado de todas las estaciones
    stations, last_updated = client.get_stations_status()

    if stations:
        # Mostrar información sobre el conjunto de datos
        print(f"Datos actualizados: {datetime.fromtimestamp(last_updated) if last_updated else 'Desconocido'}")
        print(f"Total de estaciones: {len(stations)}")

        # Mostrar estaciones operativas
        operational = client.get_operational_stations()
        print(f"\nEstaciones operativas: {len(operational)} de {len(stations)}")

        # Mostrar estaciones con bicicletas disponibles
        with_bikes = client.get_stations_with_available_bikes(min_bikes=5)
        print(f"\nEstaciones con al menos 5 bicicletas: {len(with_bikes)}")

        # Mostrar detalles de algunas estaciones
        if stations:
            print("\nDetalle de algunas estaciones:")
            for station in stations[:3]:  # Mostrar solo las primeras 3
                print(f"\n{station}")
                bikes_by_type = station.get_available_bikes_by_type()
                for bike_type, count in bikes_by_type.items():
                    print(f"  - {bike_type}: {count} disponibles")
    else:
        print("No se pudieron obtener los datos de las estaciones.")

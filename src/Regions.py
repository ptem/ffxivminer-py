from dataclasses import dataclass, asdict
from typing import List

import pandas

import JSONUtils

regions = pandas.DataFrame({
    'Region_ID': [1, 2, 3, 4, 7],
    'Region_Name': ["Japan", "North America", "Europe", "Oceania", "NA Cloud"]
})

@dataclass
class DataCenter:
    datacenter_id: int
    datacenter_name: str
    worlds: List[str]

    def __post_init__(self):
        self.datacenter_id = int(self.datacenter_id)

@dataclass
class Region:
    region_id: int
    region_name: str
    datacenters: List[DataCenter]

    def __post_init__(self):
        self.region_id = int(self.region_id)

@dataclass
class Regions:
    regions: List[Region]

    def to_json(self):
        return JSONUtils.encode_as_json(asdict(self), skip_nones=True)
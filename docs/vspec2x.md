# VSPEC2X Documentation

## Introduction

`vspec2x.py` is a tool that parses and expands VSS into different output formats.
Currently supported output formats include CSV, JSON, Yaml and a VSS binary format.


```
usage: vspec2x.py [-h] [-I dir] [-s] [--abort-on-non-core-attribute] [--abort-on-name-style] [--format format] [--no-uuid] [-o overlays] [--json-pretty] <vspec_file> <output_file>
```

Detailed information on supported arguments are available by the help (`-h`) argument.

```
user@mymachine:~/vss-tools$ ./vspec2x.py -h

```
A typical usage of the tool to generate a CSV representation of the VSS catalog is shown below.

```
user@mymachine:~/vehicle_signal_specification$ vss-tools/vspec2x.py --format csv spec/VehicleSignalSpecification.vspec res.csv
Output to csv format
Loading vspec from spec/VehicleSignalSpecification.vspec...
Calling exporter...
Generating CSV output...
All done.
```

Common for all output formats is that the VSS tree specified as input is expanded and then printed according to the selected format.

## CSV generation

The CSV generator produces one comma separated line for each branch/signal, like in the example below.

```
"Signal","Type","DataType","Deprecated","Unit","Min","Max","Desc","Comment","Allowed","Id"
"Vehicle","branch","","","","","","High-level vehicle data.","","","ccc825f94139544dbb5f4bfd033bece6"
"Vehicle.VersionVSS","branch","","","","","","Supported Version of VSS.","","","9a687e56f1305eedb20f6a021ea58f48"
"Vehicle.VersionVSS.Major","attribute","uint32","","","","","Supported Version of VSS - Major version.","","","5edf1a338c975cbb84d4ce3cfe1aa4b4"
...
```

`vspec2csv.py` can be used as a shortcut instead of `vspec2x.py --format csv`.

## JSON generation

The JSON generator produces a JSON representation of the VSS tree. For pretty printing the argument `--json-pretty` must be used.

```
  "Vehicle": {
    "children": {
      "ADAS": {
        "children": {
          "ABS": {
            "children": {
              "IsEnabled": {
                "datatype": "boolean",
                "description": "Indicates if ABS is enabled. True = Enabled. False = Disabled.",
                "type": "actuator",
                "uuid": "cad374fbfdc65df9b777508f04d5b073"
...
```

`vspec2json.py` can be used as a shortcut instead of `vspec2x.py --format json`.


## Yaml generation

The Yaml generator produces an expanded Yaml representation of the VSS tree.

```
Vehicle:
  description: High-level vehicle data.
  type: branch
  uuid: ccc825f94139544dbb5f4bfd033bece6

Vehicle.ADAS:
  description: All Advanced Driver Assist Systems data.
  type: branch
  uuid: 14c2b2e1297b513197d320a5ce58f42e

Vehicle.ADAS.ABS:
  description: Antilock Braking System signals.
  type: branch
  uuid: 219270ef27c4531f874bbda63743b330

Vehicle.ADAS.ABS.IsEnabled:
  datatype: boolean
  description: Indicates if ABS is enabled. True = Enabled. False = Disabled.
  type: actuator
  uuid: cad374fbfdc65df9b777508f04d5b073
  
...
```

`vspec2yaml.py` can be used as a shortcut instead of `vspec2x.py --format yaml`.

## Binary generation

The binary generator produces a binary file which can be used by the [vss-tools binary framework](../binary/README.md).

`vspec2binary.py` can be used as a shortcut instead of `vspec2x.py --format binary`.

## Layer Management

`vspec2x.py` supports overlays - the possibility to add layers to VSS to extend or redefine the standard VSS tree.
This can be used to customize a VSS tree to fit the signals needed for a specific vehicle.
A layer is added by the `-o <vspec.file>` argument to `vspec2x.py`. It is possible to add multiple layers.
Each layer must be a "complete" signal specification following VSS syntax.

### Example

A hypothetical example for adapting VSS to a motorcyle is given below. 

One layer has been defined in the file `file1.vspec` to add a signal to the transmission tree:

```
Vehicle:
  type: branch


Vehicle.Powertrain:
  type: branch
  description: Powertrain.

Vehicle.Powertrain.Transmission:
  type: branch
  description: Transmission

# Add a signal that does not exist in standard VSS
Vehicle.Powertrain.Transmission.FinalDrive:
  datatype: string
  type: attribute
  allowed: ['CHAIN', 'BELT', 'SHAFT']
  description: Drive type.
```

Another layer has been defined in the file `file2.vspec` to modify wheel representation and add a signal in the brake tree:

```
Vehicle:
  type: branch

Vehicle.Chassis:
  type: branch
  description: Chassis for motorbike.

Vehicle.Chassis.Axle:
  instances:
    - Row[1,2]
  type: branch
  description: Axle signals

# Changing instantiation of Wheel. Standard VSS use "Left" and "Right"
Vehicle.Chassis.Axle.Wheel:
  instances: ["Center"]
  type: branch
  description: Wheel signals for axle

Vehicle.Chassis.Axle.Wheel.Brake:
  type: branch
  description: Brake signals for wheel

# Adding a signal, not in standard VSS
# Due to changed instantiation above, this signal will in expanded tree be represented as two signals:
#
# Vehicle.Chassis.Axle.Row1.Wheel.Center.Brake.NumberOfBrakeDiscs
# Vehicle.Chassis.Axle.Row2.Wheel.Center.Brake.NumberOfBrakeDiscs
#
Vehicle.Chassis.Axle.Wheel.Brake.NumberOfBrakeDiscs:
  datatype: uint8
  type: sensor
  description: Number of brake discs on this wheel
  comment: Motorbikes often has 2 discs on the front wheel
           If the wheel has a brake drum this signal shall report 0
```

Both layers can be included in the generation by repeating the `-o` argument.

```
user@mymachine:~/vehicle_signal_specification$ vss-tools/vspec2json.py -o test.vspec -o test2.vspec spec/VehicleSignalSpecification.vspec res.json
Output to json format
Loading vspec from spec/VehicleSignalSpecification.vspec...
Applying VSS overlay from test.vspec...
Applying VSS overlay from test2.vspec...
Calling exporter...
Generating JSON output...
Serializing compact JSON...
All done.

```


### Limitations

* No support for deletion
* No warnings yet when overwriting core attributes, i.e. you can change a datatype in the VSS standard catalogue using an overlay, without getting any warning.
* No support for arbitrary metadata (accuracy, access control etc.) yet.

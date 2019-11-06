# Association Model

*`knowledge.model.association`*

description

## Configuration

### run

| parameter | type | required | default | description |
| - | - | - | - | - |
| silent | bool | no | false | choose to run model without verbose output |
| force | bool | no | false | choose to force file/table changes; no prompting |
| index | bool | no | false | create specified indexes on new tables after run complete |
| bin | int | no | 1000 | bin size for fetching items from database |
| log | str | no | null | path to where to save log output for model run |

### population

| parameter | type | required | default | description |
| - | - | - | - | - |
| size | int | yes | - | size of population to generate |
| seed | int | no | null | seed for random population generation; use null for no seed |

### items

| parameter | type | required | default | description |
| - | - | - | - | - |

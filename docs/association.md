# Association Model

*`knowledge.model.association`*

description

## Configuration

### run

| parameter | type | required | default | description |
| - | - | - | - | - |
| bin | int | no | 1000 | bin size for fetching items from database |
| cores | int | no | null | number of cores to run on; use null for autodetect |
| force | bool | no | false | choose to force file/table changes; no prompting |
| index | bool | no | false | create specified indexes on new tables after run complete |
| log | str | no | null | path to where to save log output for model run |
| silent | bool | no | false | choose to run model without verbose output |

### population

| parameter | type | required | default | description |
| - | - | - | - | - |
| rand | bool | no | true | choose to radomly sample population |
| seed | int | no | null | seed for random population generation; use null for no seed |
| size | int | yes | - | size of population to generate |
| source | str | yes | - | population source; options are "synthea" or "mimic" |

### items

| parameter | type | required | default | description |
| - | - | - | - | - |
| count_only | bool | no | false | choose to only count the number of items instead of a full model run |
| max_support | float | no | 1.0 | upper support bound for items that will kept in model run |
| min_support | float | no | 0.0 | lower support bound for items that will kept in model run |
| source | list[str] | yes | - | item source; choices include any combination of "observations", "treatments", and "conditions"; at least one is required |

### tree

| parameter | type | required | default | description |
| - | - | - | - | - |
| load | bool | no | false |  |
| pickle | str | no | null |  |
| save | bool | no | false |  |

### patterns

| parameter | type | required | default | description |
| - | - | - | - | - |
| count_only | bool | no | false |  |
| max_size | int | yes | - |  |
| max_support | float | no | 1.0 |  |
| min_support | float | no | 0.0 |  |

### associations

| parameter | type | required | default | description |
| - | - | - | - | - |
| count_only | bool | no | false |  |
| csv | str | no  | null |  |
| min_confidence | float | no | 0.0 |  |
| min_support | float | no | 0.0 |  |
| save | bool | no | false |  |

### database

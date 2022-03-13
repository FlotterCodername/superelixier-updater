from typing import Dict, List, Literal, Optional, Union

Json = Union[Dict, List]
JsonResponse = Optional[Json]
RealBool = Literal[True, False]
FlakyBool = Literal[True, False, None]

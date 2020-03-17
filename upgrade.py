
import sys
if "--upgrade-104-to-110" in sys.argv:
    from data_resource_api.backwards_compatibility.upgrade_104_to_110 import main
    main()

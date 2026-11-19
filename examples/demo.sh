#!/bin/sh
# python -m lisan, end to end.
cd "$(dirname "$0")/.."
lisan() { python -m lisan "$@"; }
echo "\$ echo 'ﷲ أكبر، مُدَرِّسَةٌ ١٢٣٫٥' | lisan normalize --profile search"
echo 'ﷲ أكبر، مُدَرِّسَةٌ ١٢٣٫٥' | lisan normalize --profile search
echo
echo "\$ echo 'والمعلمون في المدارس' | lisan tokens --stem"
echo 'والمعلمون في المدارس' | lisan tokens --stem
echo
echo "\$ echo 'مُحَمَّد' | lisan translit"
echo 'مُحَمَّد' | lisan translit
echo
echo "\$ lisan match 'عبد الرحمن بن راشد' 'Abdulrahman bin Rashid'"
lisan match 'عبد الرحمن بن راشد' 'Abdulrahman bin Rashid'; echo "exit $?"
echo
echo "\$ lisan match Hassan Hamza"
lisan match Hassan Hamza; echo "exit $?"
echo
echo "\$ echo 'ana 7abibi w gdan وصلت دلوقتي' | lisan detect"
echo 'ana 7abibi w gdan وصلت دلوقتي' | lisan detect

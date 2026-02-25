set -e

make
ssh $1 "rm /var/jb/bin/litehook_tests" || true
scp litehook_tests $1:/var/jb/bin
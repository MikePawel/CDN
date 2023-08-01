allNames=("ATL" "BOS" "DFW" "DFWDC" "DIA" "DIADC" "IAD" "LAX" "MIA" "MSP" "ORD" "PPX" "SFO")

routerNames=("ATL" "BOS" "DFW" "DIA" "IAD" "LAX" "MIA" "MSP" "ORD" "PDX" "SFO")
AS=5

for i in ${!routerNames[@]}; 
do
    curRouter="${routerNames[$i]} router"

echo "conf t
router bgp 5
network 5.200.0.0/23
"|./goto.sh $curRouter
done
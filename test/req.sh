if [[ $# -lt 3 ]]; then
	echo "Sintaxe: sh req.sh <tipo de request> <ficheiro json> <endpoint>"


	REQ=$1
	FILE="@$2"
	LINK="http://127.0.0.1:8080/dbproj/$3"

	curl -vX ${REQ} ${LINK} -d ${FILE} \
	--header "Content-Type: application/json"
fi

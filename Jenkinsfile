// Powered by Infostretch 

timestamps {

node () {

	stage ('cinema - Checkout') {
 	 checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: '', url: 'https://github.com/rayden2k6/cinema-microservice']]]) 
	}
	stage ('cinema - Build & Test') {
 			// Batch build step
bat """ 
cd services
start python bookings.py /k
start python user.py /k
start python movies.py /k
start python showtimes.py /k
ping 127.0.0.1 -n 10 > nul
cd ..
cd tests
python bookings.py
python movies.py
python showtimes.py
python user.py 
 """
		// JUnit Results
		junit 'tests/test-reports/*.xml' 
	}
}
}

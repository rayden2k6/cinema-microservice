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
start python user.py
start python movies.py
start python bookings.py
start python showtimes.py
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

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
start python user.py /k
start python movies.py /k
start python bookings.py /k
start python showtimes.py /k
timeout /t 15
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

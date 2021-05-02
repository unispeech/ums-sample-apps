
function jira(){

    this.display_name=undefined;
	this.user_name = "your jira email";
	this.password="your password";
    this.users_example=[{ "email": "gode.fire@yandex.com", "id": "123" }, { "email": "vahagn.kocharyan@unispeech.io", "id": "124" }];
	this.jira_domain="your domain";
	this.jira_project ="your jira project";



	this.getDisplayName = function(caller_id){

		
        if (caller_id != "undefined") {
			use("CURL");

			function callback(string, arg) {

				console_log("info", string);
				issues = JSON.parse(string);

			}
			var curl = new CURL();
			curl.run("GET", "https://"+this.jira_domain+"/rest/api/2/search", "jql=callerid~" + caller_id + "&project="+this.jira_project+"&maxResults=2&fields=status,reporter", callback, "my arg\n", this.user_name+":"+this.password, "500", "application/json");

			if (typeof issues != "undefined" && (issues.issues != "undefined" && issues.total > 0)) {
				this.display_name=issues.issues[0].fields.reporter.displayName;
				
			}

		}
	
    }

    this.userExist = function (number_sequence) {

        var users = this.users_example;

        for (var i = 0; i < users.length; i++) {

            if (number_sequence == users[i].id) {

                
                return this.jiraUserExist(users[i].email);
            } 
    
        }
    
    
    }


	this.jiraUserExist=function(email){

		use("CURL");

		var status=false;
		function callback(string, arg) {
    
			user = JSON.parse(string);
			console_log("ERR","got jira user"+ user);
			

		}

		var curl = new CURL();
		curl.run("GET", "https://"+this.jira_domain+"/rest/api/2/user/search", "query=" + email + "", callback, "my arg\n", this.user_name+":"+this.password, "500", "application/json");
		
		if(user!="undefined"){
			status=true;
		}

		return status;
	}


    this.issueStatus = function (issue_id) {
		use("CURL");

		if (issue_id != "undefined") {
			function callback(string, arg) {
				console_log("info", string);
				jira_issues_status = JSON.parse(string);
				
			}

			var curl = new CURL();
			curl.run("GET", "https://"+this.jira_domain+"/rest/api/2/issue/" + issue_id + "", "fields=status", callback, "my arg\n", this.user_name+":"+this.password, "500", "application/json");

			return jira_issues_status;
			
		}

		
    }
    
    
    this.openIssue = function (caller_id,message) {
		use("CURL");

		createJiraIssue();

		function my_callback(string, arg) {

			console_log("info", string);
			issue = JSON.parse(string);
			

		}
	
		function createJiraIssue() {
			var datas = {
				"fields": {
					"project":
					{
						"key": "UN"
					},
					"summary": message,
					"description": "from" + caller_id,
					"issuetype": {
						"name": "Incident"
					},
					"reporter": { "accountId": this.user[0].accountId },
					"customfield_10059": caller_id,
				}
			};

			var data = JSON.stringify(datas);

			var curl = new CURL();
			curl.run("POST", "https://"+this.jira_domain+"/rest/api/2/issue/", data, my_callback, "my arg\n", this.user_name+":"+this.password, "500", "application/json");

		}
		var issue_id = issue.id.replace(/(\d{1})/g, '$1 ').replace(/(^\s+|\s+$)/, '');

		return issue_id;


	}

}





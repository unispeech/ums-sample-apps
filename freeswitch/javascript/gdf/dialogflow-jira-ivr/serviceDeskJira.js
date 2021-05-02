include("playanddetect.js");
include("jira.js");

session.answer()

/***************** init PlayAndDetectSpeech class *****************/
app = new PlayAndDetectSpeech(session)

/***************** init jira class *****************/
jira=new jira();
jira.getDisplayName(app.getCallerid());

/***************** set main parametrs  *****************/

app.setAsrEngine("unimrcp:ums-v2");
app.setTtsEngine("unimrcp:ums-v2");
app.name=jira.display_name;
app.setProjectId(undefined);
app.composeEventGrammar("welcome");



jiraIssueState = function () {
    if (app.validation()) {

        if (app.result.action == "support.issueStatus") {

            console_log("IFO", "got issue id"+app.result.parameters.ID);
            var jira_issue_status=jira.issueStatus(app.result.parameters.ID);

            if (!jira_issue_status.errorMessages) {
                
                app.speak("your issue still " + jira_issue_status.fields.status.name);

            } else {
                console_log("IFO", jira_issue_status.errorMessages[0]);
                app.speak(jira_issue_status.errorMessages[0])
                
            }
            return true;

        } return false;
    }

    

}


CreateJiraIssue= function () {
        
    if (app.result.action == "support.problem" ) {

        if (typeof app.result.parameters["number-sequence"] != "undefined" && app.result.parameters["number-sequence"].length > 0) {

            var key=app.result.parameters["number-sequence"];

            if (jira.userExist(key)) {

                if (!app.validation()) {
                    return false;
                };

                
                var new_issue_id =jira.openIssue(app.getCallerid(),app.result.parameters.message);
                    
                app.speak("Your issue was created.your issue key is " + new_issue_id + ".Please store your issue key.");  

                
            } else {
                app.speak("Your ID is invalid.");
                
            }
            return true;
        } 
    } return false;
}

run = function(){

        app.PlayAndDetect()

        while (app.session.ready()) {

            app.composeSpeechGrammar();
            app.PlayAndDetect();
            

            if (jiraIssueState()) {
                break;
            }
            if (CreateJiraIssue()) {
                break;
            }

        }
        app.speak("Thank you. See you next time")
}        

run()



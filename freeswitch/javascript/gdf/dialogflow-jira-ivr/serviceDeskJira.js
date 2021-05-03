include("playAndDetect.js");
include("jira.js");

session.answer()

/***************** init PlayAndDetectSpeech class *****************/
app = new PlayAndDetectSpeech(session)

/***************** init jira class *****************/
jira=new jira();
jira.getDisplayName(app.getCallerid());

/***************** Set main parametrs *****************/
app.setAsrEngine("unimrcp:ums-v2");
app.setTtsEngine("unimrcp:ums-v2");
app.caller_name=jira.display_name;
app.setProjectId(undefined);
app.setOptions("{start-input-timers=false,define-grammar=false,no-input-timeout=10000,speech-language=en-US}");
app.composeEventGrammar("welcome");



/***************** Get jira issue status by issue id an speak status name *****************/
jiraIssueState = function () {
    if (app.validation()) {

        if (app.result.action == "support.issueStatus") {

            console_log("IFO", "got id from google dialogflow"+app.result.parameters.ID);
            var jira_issue_status=jira.issueStatus(app.result.parameters.ID);

            if (!jira_issue_status.errorMessages) {
                
                app.speak("Your issue still " + jira_issue_status.fields.status.name);

            } else {
                console_log("IFO", jira_issue_status.errorMessages[0]);
                app.speak(jira_issue_status.errorMessages[0])
                
            }
            return true;

        } return false;
    }

    

}

/*****************  If jira user exists create jira issue. *****************/
createJiraIssue= function () {
        
    if (app.result.action == "support.problem" ) {

        if (typeof app.result.parameters["number-sequence"] != "undefined" && app.result.parameters["number-sequence"].length > 0) {

            var key=app.result.parameters["number-sequence"];

            if (jira.userExist(key)) {

                if (!app.validation()) {
                    return false;
                };

                
                var new_issue_id =jira.openIssue(app.getCallerid(),app.result.parameters.message);
                    
                app.speak("Your issue was created.your issue key is " + new_issue_id + ".Please store your issue key.Your issue key is " + new_issue_id + ".");  

                
            } else {
                app.speak("Your ID is invalid.");
                
            }
            return true;
        } 
    } return false;
}


/*****************  Main function. *****************/
run = function(){

        /*****************  init event . *****************/
        app.playAndDetect()
        /*****************  Main recognition loop *****************/
        while (app.session.ready()) {

            app.composeSpeechGrammar();
            app.playAndDetect();
            

            if (jiraIssueState()) {
                break;
            }
            if (createJiraIssue()) {
                break;
            }

        }
         /*****************  Speak the final message *****************/
        app.speak("Thank you. See you next time")
}        

run()



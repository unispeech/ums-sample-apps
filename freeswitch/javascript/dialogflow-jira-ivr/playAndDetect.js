
function PlayAndDetectSpeech(session) {
	this.session = session;
    this.asr_engine;
    this.tts_engine;
    this.tts_voice;
    this.lang="en-US";
    this.display_name;
    this.result;
    this.str="";
    this.jira = new jira();
    this.inputVar;
    this.event_grammar="builtin:event/";
    this.speech_grammar="builtin:speech/transcribe";
    this.dtmf_grammar="builtin:dtmf/digits";
    this.separator="?";
    this.grammar = undefined;
    this.project_id=undefined;
    this.name=undefined;
    
	this.setAsrEngine = function (asr_engine) {
		this.asr_engine = asr_engine;
    }
    this.composeTtsOptions = function(){
        return ttsoptions="{speech-language="+this.lang+"}";
    }
    this.composeRecogOptions = function(){
        return recogOptions="{start-input-timers=true,define-grammar=false,no-input-timeout=10000,speech-language="+this.lang+"}";
    }
	this.setTtsEngine = function (tts_engine) {
		this.tts_engine = tts_engine;
		this.session.setVariable("tts_engine",tts_engine)
    }
    this.setTtsVoice = function (tts_voice) {
		this.tts_voice = tts_voice;
		this.session.setVariable("tts_voice",tts_voice)
    }

    this.setProjectId=function(project_id){
        this.project_id=project_id;
    }
    

    this.Options= function(options){
        this.options = options;
    }
    this.getCallerid = function(){
        return this.session.getVariable("caller_id_number");
    }
    
    
    this.composeEventGrammar= function (intent,parameterName,parameterValue){
        // var grammar = this.composeRecogOptions() + this.event_grammar;
             
        this.grammar= this.composeRecogOptions()+this.event_grammar;

        if (intent){
            this.grammar+=intent+this.separator;
        }
        if (this.name){
            this.separator=";"
            this.appendGrammarParametr("name",this.name);
        }
        if(this.project_id){
            this.separator=";"
            this.appendGrammarParametr("projectid",this.project_id);
        }
        if(parameterName&&parameterValue){
            this.separator=";"
            this.appendGrammarParametr(parameterName,parameterValue);
        }
        
        
    }

    this.composeSpeechGrammar = function(parameterName,parameterValue){
        this.separator="?"
        this.grammar = this.composeRecogOptions() + this.dtmf_grammar+this.separator+"\n"+this.speech_grammar+this.separator;
        if(this.project_id){
            this.separator=";"
            this.appendGrammarParametr("projectid",this.project_id);
        }
        if(parameterName&&parameterValue){
            this.separator=";"
            this.appendGrammarParametr(parameterName,parameterValue);
        }
    }

    this.appendGrammarParametr= function(parameterName,parameterValue){
        this.grammar += parameterName+"="+parameterValue+this.separator;
        console_log("INFO","current grammar is "+this.grammar);
        
    }

	this.PlayAndDetect = function () {
                
        if (this.str!="undefined"){
            
            data = "say:"+this.composeTtsOptions()+this.str + " " + "detect:" + this.asr_engine + " " + this.grammar
            this.session.execute("play_and_detect_speech",data);
            this.CollectResult();
            if (this.result.fulfillmentText != undefined){
                this.str = this.result.fulfillmentText;
            }
                     
        }
		

	}
    this.speak = function (str) {
		return this.session.speak(this.tts_engine, "", str);
    }
    
    this.CollectResult = function () {

		if (this.session.getVariable("detect_speech_result").indexOf("{") == 0) {
			console_log("ERR",this.session.getVariable("detect_speech_result").indexOf("{"));
			var jsonResult = this.session.getVariable("detect_speech_result");
			if (typeof jsonResult != "undefined") {
				if (jsonResult.indexOf("Completion-Cause:") == -1) {

					result = JSON.parse(jsonResult);
					consoleLog("ERR", typeof result);
					if (typeof result != "undefined") {
						this.result = result;
						console_log("ERR", result.fulfillmentText);
						var strObj = JSON.stringify(result);
						console_log("ERR", strObj);
						return this.result;
					}

				}
				else {
					consoleLog("INFO", "Recognition completed abnormally!no json result\n");
					// console_log("ERR", "modUnispeech 177 line");
				}
			}
			else {
				consoleLog("INFO", "No result!\n");

			}

			console_log("ERR", strObj);

		} 
        else {
			consoleLog("INFO", "No json result!\n");
		}

    }
    
    

    this.validation = function () {

        var allPresent = this.result.allRequiredParamsPresent;
        if (typeof allPresent != "undefined") {
            consoleLog("IFO", this.result.action);
            if (allPresent && (this.result.action != "input.welcome" && this.result.action != "input.unknown")) {
                return true;
            }
            return false;
    
        }return false;
    }
   
    
    

    
    
}
   






function PlayAndDetectSpeech(session) {
	this.session = session;
    this.asr_engine;
    this.tts_engine;
    this.tts_voice;
    this.options;
    this.result;
    this.str="";
    this.inputVar;
    this.event_grammar="builtin:event/";
    this.speech_grammar="builtin:speech/transcribe";
    this.separator="?";
    this.grammar = undefined;
    this.project_id=undefined;
    this.caller_name=undefined;
    
	this.setAsrEngine = function (asr_engine) {
		this.asr_engine = asr_engine;
    }
    this.setLanguge= function (language) {
		this.lang = language;
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
    
    this.setOptions= function(options){
        this.options = options;
    }
    this.getCallerid = function(){
        return this.session.getVariable("caller_id_number");
    }
    this.speak = function (str) {
		return this.session.speak(this.tts_engine, "", str);
    }
    
    this.composeEventGrammar= function (intent,parameterName,parameterValue){
             
        this.grammar= this.options+this.event_grammar;

        if (intent){
            this.grammar+=intent+this.separator;
        }
        if (this.caller_name){
            this.separator=";"
            this.appendGrammarParametr("name",this.caller_name);
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
        this.grammar = this.options+this.speech_grammar+this.separator;
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

	this.playAndDetect = function () {
                
        if (this.str!="undefined"){
            
            data = "say:"+this.str + " " + "detect:" + this.asr_engine + " " + this.grammar
            this.session.execute("play_and_detect_speech",data);
            this.CollectResult();
            if (this.result.fulfillmentText != undefined){
                this.str = this.result.fulfillmentText;
            }
                     
        }
		

	}
    
    
    this.CollectResult = function () {

		var jsonResult = this.session.getVariable("detect_speech_result");
			if (typeof jsonResult != "undefined") {
				if (jsonResult.indexOf("Completion-Cause:") == -1) {

					result = JSON.parse(jsonResult);
					
					if (typeof result != "undefined") {
						this.result = result;
						
						var strObj = JSON.stringify(result);
						console_log("INFO","got result"+ strObj);
					}

				}
				else {
					consoleLog("INFO", "Recognition completed abnormally!no json result\n");
					
				}
			}
			else {
				consoleLog("INFO", "No result!\n");

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
   





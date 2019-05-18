import azure.cognitiveservices.speech as speechsdk

speech_key, service_region = "4c80a4fb678f438eb068f0e22fbf076e", "southcentralus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language="en-IN")
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

def AzureListening():
    print("azure listening...")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    return None

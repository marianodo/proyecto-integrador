// We make use of this 'server' variable to provide the address of the
// REST Janus API. By default, in this example we assume that Janus is
// co-located with the web server hosting the HTML pages but listening
// on a different port (8088, the default for HTTP in Janus), which is
// why we make use of the 'window.location.hostname' base address. Since
// Janus can also do HTTPS, and considering we don't really want to make
// use of HTTP for Janus if your demos are served on HTTPS, we also rely
// on the 'window.location.protocol' prefix to build the variable, in
// particular to also change the port used to contact Janus (8088 for
// HTTP and 8089 for HTTPS, if enabled).
// In case you place Janus behind an Apache frontend (as we did on the
// online demos at http://janus.conf.meetecho.com) you can just use a
// relative path for the variable, e.g.:
//
// 		var server = "/janus";
//
// which will take care of this on its own.
//
//
// If you want to use the WebSockets frontend to Janus, instead, you'll
// have to pass a different kind of address, e.g.:
//
// 		var server = "ws://" + window.location.hostname + ":8188";
//
// Of course this assumes that support for WebSockets has been built in
// when compiling the gateway. WebSockets support has not been tested
// as much as the REST API, so handle with care!
//
//
// If you have multiple options available, and want to let the library
// autodetect the best way to contact your gateway (or pool of gateways),
// you can also pass an array of servers, e.g., to provide alternative
// means of access (e.g., try WebSockets first and, if that fails, fall
// back to plain HTTP) or just have failover servers:
//
//		var server = [
//			"ws://" + window.location.hostname + ":8188",
//			"/janus"
//		];
//
// This will tell the library to try connecting to each of the servers
// in the presented order. The first working server will be used for
// the whole session.
//

var server = null;
if(window.location.protocol === 'http:')
	server = "http://" + window.location.hostname + ":8090/janus";
else
	server = "https://" + window.location.hostname + ":8091/janus";

var janus = null;
var sipcall = null;
var started = false;
var spinner = null;

var registered = false;

var incoming = null;


$(document).ready(function() {
	
	// Initialize the library (console debug enabled)
	Janus.init({debug: true, callback: function() {
		// Use a button to start the demo

		$('#start').click(function() {
			//$.get("activeRelay",{status:"on"}, function(response){});
			$.get("activeRelay/on",function(response){});
			if(started){
				
				return;}
			started = true;
			$(this).attr('disabled', true).unbind('click');
			// Make sure the browser supports WebRTC
			if(!Janus.isWebrtcSupported()) {
				bootbox.alert("No WebRTC support... ");
				return;
			}
			// Create session
			janus = new Janus(
				{
					server: server,
					success: function() {
						// Attach to echo test plugin
						janus.attach(
							{
								plugin: "janus.plugin.sip",
								success: function(pluginHandle) {
									$('#details').remove();
									sipcall = pluginHandle;
									console.log("Plugin attached! (" + sipcall.getPlugin() + ", id=" + sipcall.getId() + ")");
									// Prepare the username registration
									$('#sipcall').removeClass('hide').show();
									$('#login').removeClass('hide').show();
									registerUsername();
									$('#server').focus();
									$('#cartelPuerta').removeClass('hide').show();
									$('#start').removeAttr('disabled').html("Stop")
									
										.click(function() {
											$(this).attr('disabled', true);
											janus.destroy();
										});

									$('#guest').change(function() {
										if($('#guest').length && $('#guest:checked').val() !== undefined) {
											//~ $('#username').empty().attr('disabled', true);
											$('#password').empty().attr('disabled', true);
										} else {
											//~ $('#username').removeAttr('disabled');
											$('#password').removeAttr('disabled');
										}
									});
								},
								error: function(error) {
									console.log("  -- Error attaching plugin... " + error);
									bootbox.alert("  -- Error attaching plugin... " + error);
								},
								consentDialog: function(on) {
									console.log("Consent dialog should be " + (on ? "on" : "off") + " now");
									if(on) {
										// Darken screen and show hint
										$.blockUI({ 
											message: '<div><img src="/static/img/up_arrow.png"/></div>',
											css: {
												border: 'none',
												padding: '15px',
												backgroundColor: 'transparent',
												color: '#aaa',
												top: '10px',
												left: (navigator.mozGetUserMedia ? '-100px' : '300px')
											} });
									} else {
										// Restore screen
										$.unblockUI();
									}
								},
								onmessage: function(msg, jsep) {
									console.log(" ::: Got a message :::");
									console.log(JSON.stringify(msg));
									
									// Any error?
									var error = msg["error"];
									if(error != null && error != undefined) {
										if(!registered) {
											$('#server').removeAttr('disabled');
											$('#username').removeAttr('disabled');
											$('#password').removeAttr('disabled');
											$('#register').removeAttr('disabled').click(registerUsername);
											$('#guest').removeAttr('disabled').attr('checked', false);
										}
										bootbox.alert(error);
										return;
									}
									var result = msg["result"];
									if(result !== null && result !== undefined && result["event"] !== undefined && result["event"] !== null) {
										var event = result["event"];
										if(event === 'registered') {
											console.log("Successfully registered as " + result["username"] + "!");
											$('#you').removeClass('hide').show().text("Registered as '" + result["username"] + "'");
											// TODO Enable buttons to call now
											if(!registered) {
												registered = true;
												$('#phone').removeClass('hide').show();
												$('#call').unbind('click').click(doCall);
												$('#peer').focus();
											}
										} else if(event === 'calling') {
											console.log("Waiting for the peer to answer...");
											// TODO Any ringtone?
										} else if(event === 'incomingcall') {
											console.log("Incoming call from " + result["username"] + "!");
											var doAudio = true, doVideo = false;
											if(jsep !== null && jsep !== undefined) {
												// What has been negotiated?
												doAudio = (jsep.sdp.indexOf("m=audio ") > -1);
												doVideo = (jsep.sdp.indexOf("m=video ") > -1);
												console.log("Audio " + (doAudio ? "has" : "has NOT") + " been negotiated");
												console.log("Video " + (doVideo ? "has" : "has NOT") + " been negotiated");
											}
											// Notify user
											bootbox.hideAll();
											incoming = bootbox.dialog({
												message: "Incoming call from " + result["username"] + "!",
												title: "Incoming call",
												closeButton: false,
												buttons: {
													success: {
														label: "Answer",
														className: "btn-success",
														callback: function() {
															incoming = null;
															$('#peer').val(result["username"]).attr('disabled', true);
															sipcall.createAnswer(
																{
																	jsep: jsep,
																	media: { audio: doAudio, video: doVideo },
																	success: function(jsep) {
																		console.log("Got SDP! audio=" + doAudio + ", video=" + doVideo);
																		console.log(jsep);
																		var body = { "request": "accept" };
																		sipcall.send({"message": body, "jsep": jsep});
																		$('#call').removeAttr('disabled').html('Hangup')
																			.removeClass("btn-success").addClass("btn-danger")
																			.unbind('click').click(doHangup);
																	},
																	error: function(error) {
																		console.log("WebRTC error:");
																		console.log(error);
																		bootbox.alert("WebRTC error... " + JSON.stringify(error));
																		// Don't keep the caller waiting any longer
																		var body = { "request": "decline" };
																		sipcall.send({"message": body});
																	}
																});
														}
													},
													danger: {
														label: "Decline",
														className: "btn-danger",
														callback: function() {
															incoming = null;
															var body = { "request": "decline" };
															sipcall.send({"message": body});
														}
													}
												}
											});											
										} else if(event === 'accepted') {

											console.log(result["username"] + " accepted the call!");
											// TODO Video call can start
											if(jsep !== null && jsep !== undefined) {
												sipcall.handleRemoteJsep({jsep: jsep, error: doHangup });
											}
											$('#call').removeAttr('disabled').html('Hangup')
												.removeClass("btn-success").addClass("btn-danger")
												.unbind('click').click(doHangup);
												
												
										} else if(event === 'hangup') {

											if(incoming != null) {
												incoming.modal('hide');
												incoming = null;
											}
											console.log("Call hung up by " + result["username"] + " (" + result["reason"] + ")!");
											bootbox.alert(result["reason"]);
											// Reset status
											sipcall.hangup();
											$('#peer').removeAttr('disabled').val('');
											$('#call').removeAttr('disabled').html('Call')
												.removeClass("btn-danger").addClass("btn-success")
												.unbind('click').click(doCall);
										}
									}
								},
								onlocalstream: function(stream) {
									console.log(" ::: Got a local stream :::");
									console.log(JSON.stringify(stream));
									$('#videos').removeClass('hide').show();
									if($('#myvideo').length === 0)
										$('#videoleft').append('<video class="rounded centered" id="myvideo" width=320 height=240  muted="muted"/>');
									attachMediaStream($('#myvideo').get(0), stream);
									// No remote video yet
									$('#myvideo').remove();
									$('#videoright').append('<video class="rounded centered" id="waitingvideo" width=320 height=240   />');
									if(spinner == null) {
										var target = document.getElementById('videoright');
										spinner = new Spinner({top:100}).spin(target);
									} else {
										spinner.spin();
									}
								},
								onremotestream: function(stream) {
									console.log(" ::: Got a remote stream :::");
									console.log(JSON.stringify(stream));
									spinner.stop();
									$('#waitingvideo').remove();
									if($('#remotevideo').length === 0) {
										$('#videoright').append(
											'<div>DTMF: <div id="dtmf" class="btn-group btn-group-xs"></div></div>' +
											'<video class="rounded centered" id="remotevideo" width=320 height=240 autoplay/>');
										//for(var i=0; i<12; i++) {
											//if(i<10)
											//	$('#dtmf').append('<button class="btn btn-info dtmf">' + i + '</button>');
											//else if(i == 10)
											//	$('#dtmf').append('<button class="btn btn-info dtmf">#</button>');
										//	else if(i == 11)
											//	$('#dtmf').append('<button class="btn btn-info dtmf">*</button>');
										//}
										$('.dtmf').click(function() {
											// Send DTMF tone
											sipcall.dtmf({dtmf: { tones: $(this).text()}});
										});
									}
									attachMediaStream($('#remotevideo').get(0), stream);
								},
								oncleanup: function() {
									console.log(" ::: Got a cleanup notification :::");
									$('#myvideo').remove();
									$('#waitingvideo').remove();
									$('#remotevideo').remove();
									$('#videos').hide();
									$('#dtmf').parent().remove();
								}
							});
					},
					error: function(error) {
						console.log(error);
						bootbox.alert(error, function() {
							window.location.reload();
						});
					},
					destroyed: function() {
						$.get("activeRelay/off",function(response){});
						window.location.reload();
					}
				});
		});
	}});

});
	
function checkEnter(field, event) {
	var theCode = event.keyCode ? event.keyCode : event.which ? event.which : event.charCode;
	if(theCode == 13) {
		if(field.id == 'server' || field.id == 'username' || field.id == 'password')
			registerUsername();
		else if(field.id == 'peer')
			doCall();
		return false;
	} else {
		return true;
	}
}

function registerUsername() {
	
	var sipserver = "sip:192.168.1.50";
	var username = "sip:6001@192.168.1.50";
	var password = "asterisk";
	var register = {
		"request" : "register",
		"username" : username,
		"secret" : password,
		"proxy" : sipserver
	};
	sipcall.send({"message": register});
	doCall();
}

function doCall() {
	// Call someone
	
	var username = "sip:6000@192.168.1.50";
	
	// Call this URI
	doVideo = ($('#dovideo:checked').val() === false);
	console.log("This is a SIP " + (doVideo ? "video" : "audio") + " call (dovideo=" + doVideo + ")"); 
	sipcall.createOffer(
		{
			media: {
				audioSend: true, audioRecv: true,		// We DO want audio
				videoSend: false, videoRecv: false	// We MAY want video
			},
			success: function(jsep) {
				console.log("Got SDP!");
				console.log(jsep);
				var body = { "request": "call", uri: "sip:6000@192.168.1.50" };
				sipcall.send({"message": body, "jsep": jsep});
			},
			error: function(error) {
				console.log("WebRTC error...");
				console.log(error);
				bootbox.alert("WebRTC error... " + JSON.stringify(error));
			}
		});
}

function doHangup() {
	// Hangup a call
	$('#call').attr('disabled', true).unbind('click');
	var hangup = { "request": "hangup" };
	sipcall.send({"message": hangup});
	sipcall.hangup();
}

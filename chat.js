var chat = (function() {
	var socket;

	function init() {
		var host = "ws://127.0.0.1:8080"
		try {
			socket = new WebSocket(host);
			socket.onopen = function(msg) {
				console.log('open...' + msg.data);
			}
			socket.onmessage = function(msg) {
				console.log(msg.data);
				$('.chat_room').value += msg.data;
			}
			socket.onclose = function(msg) {
				console.log('close...' + msg);
			}
		} catch (ex) {
			console.log(ex);
		}
	}

	function sendMessage() {
		var $msg = $('#msg')[0];
		var msg = $msg.value;
		var $chat_room = $('.chat_room')[0];
		try {
			socket.send(msg);
		} catch(ex) {
			console.log(ex);
		}
		$msg.value = "";
		$msg.focus();
	}

	function chat() {
		init();
		$('#send').on('click', function() {
			sendMessage();
		});
		$('#close').on('click', function() {
			socket.onclose();
		});
	}

	return {
		chat: chat
	};
})();

$(function() {
	chat.chat();
});
var Logging = function(level) {
    this.messages = [];
    this.level = (typeof level !== 'undefined'? level: Logging.WARNING);
};

Logging.INFO = 2;
Logging.WARNING = 1;
Logging.ERROR = 0;


Logging.prototype.add = function(level, parentUrl, url, status_,  message) {
    this.messages.push({
        level: level,
        parentUrl: parentUrl,
        url: url,
        'status': status_,
        message: message,
    });
};

Logging.prototype.info = function() {
    var args = Array.prototype.slice.call(arguments);
    args.unshift(Logging.INFO);
    this.add.apply(this, args);
};


Logging.prototype.warning = function() {
    var args = Array.prototype.slice.call(arguments);
    args.unshift(Logging.WARNING);
    this.add.apply(this, args);
};


Logging.prototype.error = function() {
    var args = Array.prototype.slice.call(arguments);
    args.unshift(Logging.ERROR);
    this.add.apply(this, args);
};


Logging.prototype.display = function() {
    for (var i=0, len=this.messages.length; i < len; i++) {
        if (this.messages[i].level <= this.level) {
            console.log(JSON.stringify(this.messages[i], undefined, 4));
        }
    }
};


exports.Logging = Logging;

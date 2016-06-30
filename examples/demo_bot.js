/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
           ______     ______     ______   __  __     __     ______
          /\  == \   /\  __ \   /\__  _\ /\ \/ /    /\ \   /\__  _\
          \ \  __<   \ \ \/\ \  \/_/\ \/ \ \  _"-.  \ \ \  \/_/\ \/
           \ \_____\  \ \_____\    \ \_\  \ \_\ \_\  \ \_\    \ \_\
            \/_____/   \/_____/     \/_/   \/_/\/_/   \/_/     \/_/


This is a sample Slack bot built with Botkit.

This bot demonstrates many of the core features of Botkit:

* Connect to Slack using the real time API
* Receive messages based on "spoken" patterns
* Send a message with attachments
* Send a message via direct message (instead of in a public channel)

# RUN THE BOT:

  Get a Bot token from Slack:

    -> http://my.slack.com/services/new/bot

  Run your bot from the command line:

    token=<MY TOKEN> node demo_bot.js

# USE THE BOT:

  Find your bot inside Slack to send it a direct message.

  Say: "Hello"

  The bot will reply "Hello!"

  Say: "Attach"

  The bot will send a message with a multi-field attachment.

  Send: "dm me"

  The bot will reply with a direct message.

  Make sure to invite your bot into other channels using /invite @<my bot>!

# EXTEND THE BOT:

  Botkit has many features for building cool and useful bots!

  Read all about it here:

    -> http://howdy.ai/botkit

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
var PythonShell = require('python-shell');
var Botkit = require('../lib/Botkit.js');

if (!process.env.token) {
  console.log('Error: Specify token in environment');
  process.exit(1);
}

var controller = Botkit.slackbot({
 debug: false
});

controller.spawn({
  token: process.env.token
}).startRTM(function(err) {
  if (err) {
    throw new Error(err);
  }
});

controller.hears('another_keyword','direct_message,direct_mention',function(bot,message) {
  var reply_with_attachments = {
    'username': 'Cuty' ,
    'text': 'This is a pre-text',
    "attachments": [
       {
           "fallback": "Required plain-text summary of the attachment.",
           "color": "#36a64f",
           "pretext": "Optional text that appears above the attachment block",
           "author_name": "cuty",
           "author_link": "http://flickr.com/bobby/",
           "author_icon": "http://flickr.com/icons/bobby.jpg",
           "title": "Documentation",
           "title_link": "https://api.slack.com/",
           "text": "This is an attachment",
           "fields": [
               {
                   "title": "Fields",
                   "value": "value",
                   "short": false
               }
           ],
           "image_url": "https://www.nasa.gov/sites/default/files/styles/full_width_feature/public/thumbnails/image/darksideimage_unann.png?itok=JFXuOSqu",
           "footer": "Star",
           "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
           "ts": 123456789
       }
   ]

    }

  bot.reply(message, reply_with_attachments);
});

controller.hears(['.*[H|h]ello.*|.*[H|h]i.*'],['direct_message','direct_mention','mention'],function(bot,message) {
  controller.storage.users.get(message.user, function(err, user) {
        if (user && user.name) {
            bot.reply(message, 'Hi~ ' + user.name);
        }
       else {
            bot.startConversation(message, function(err, convo) {
                if (!err) {
                    convo.say('Hi~It is Cuty! I do not know your name yet!');
                    convo.ask('What should I call you?', function(response, convo) {
                      var start_is = response.text.indexOf('name is');
                      var start_me = response.text.indexOf('call me');
                      if(start_is != -1){
                        response.text= response.text.substring(start_is+8);
                      }
                      else if(start_me != -1){
                        response.text = response.text.substring(start_me+8);
                      }
                        convo.ask('You want me to call you `' + response.text + '`?', [
                            {
                                pattern: 'yes',
                                callback: function(response, convo) {
                                    // since no further messages are queued after this,
                                    // the conversation will end naturally with status == 'completed'
                                    convo.next();
                                }
                            },
                            {
                                pattern: 'no',
                                callback: function(response, convo) {
                                    // stop the conversation. this will cause it to end with status == 'stopped'
                                    convo.stop();
                                }
                            },
                            {
                                default: true,
                                callback: function(response, convo) {
                                    //convo.repeat();
                                    convo.next();
                                }
                            }
                        ]);

                        convo.next();

                    }, {'key': 'nickname'}); // store the results in a field called nickname

                    convo.on('end', function(convo) {
                        if (convo.status == 'completed') {
                            controller.storage.users.get(message.user, function(err, user) {
                                if (!user) {
                                    user = {
                                        id: message.user,
                                    };
                                }
                                user.name = convo.extractResponse('nickname');
                                controller.storage.users.save(user, function(err, id) {
                                    bot.reply(message, 'Got it. I will call you ' + user.name + ' from now on.');
                                });
                            });



                        } else {
                            // this happens if the conversation ended prematurely for some reason
                            bot.reply(message, 'OK, nevermind!');
                        }
                    });
                }
            });
        }
    });
});

controller.hears(['.*function.*'],['direct_message','direct_mention','mention'],function(bot,message) {
  controller.storage.users.get(message.user, function(err, user) {
       bot.reply(message,"I can do a lot of things. You can ask me about your balance and transaction history. What can I do for you "+ user.name+"?");
     });
});
controller.on('direct_mention',function(bot,message) {
  // reply to _message_ by using the _bot_ object
  bot.reply(message,'Hi, this is Cuty. What could I do for you?');
});

controller.hears(['python'],['direct_message','direct_mention','mention'],function(bot,message) {
  PythonShell.run('Parser/Parser.py', function (err,results) {
    if (err)
        bot.reply(message,"Your query is invalid");
        bot.reply(message,results[0]);
    console.log(results);
  });
});

controller.hears(['.*'],['direct_message','direct_mention','mention'],function(bot,message) {
       console.log(message.text);
       console.log(message.type);
       bot.reply(message,"mention");
});



controller.hears(['attach'],['direct_message','direct_mention'],function(bot,message) {

  var attachments = [];
  var attachment = {
    title: 'This is an attachment',
    color: '#FFCC99',
    fields: [],
  };

  attachment.fields.push({
    label: 'Field',
    value: 'A longish value',
    short: false,
  });

  attachment.fields.push({
    label: 'Field',
    value: 'Value',
    short: true,
  });

  attachment.fields.push({
    label: 'Field',
    value: 'Value',
    short: true,
  });

  attachments.push(attachment);

  bot.reply(message,{
    text: 'See below...',
    attachments: attachments,
  },function(err,resp) {
    console.log(err,resp);
  });
});

controller.hears(['dm me'],['direct_message','direct_mention'],function(bot,message) {
  bot.startConversation(message,function(err,convo) {
    convo.say('Heard ya');
  });

  bot.startPrivateConversation(message,function(err,dm) {
    dm.say('Private reply!');
  });

});

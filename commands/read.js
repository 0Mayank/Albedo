const { RichEmbed } = require("discord.js");

exports.run = async (client, msg, args, color) => {
    let nick = msg.member.nickname !== null ? `${msg.member.nickname}` : msg.author.username;
    let id = args[0];
  
    if (!msg.channel.nsfw) return msg.channel.send(`NSFW channel please.`).then(msg => msg.delete(5000));
    if (!args[0]) return msg.channel.send(`**${nick}**, please give me the doujin ID`).then(msg => msg.delete(5000));
  
    try {
        let m = await client.embeds.getInfoEmbed(id, msg);
        // client.embeds.getEmoji(id, m, msg);
    } catch (e) {
        if (e.message == 'Doujin Not Found') {
            return msg.channel.send(`**${nick}**, I can't find the doujin that you mean`).then(msg => msg.delete(5000));
        }
    }
}

exports.conf = {
  aliases: [],
  cooldown: '15'
}

exports.help = {
  name: 'read',
  description: 'Read nHentai manga from Discord',
  usage: 'read <Book_ID>'
}

const { Collection } = require("discord.js");
const cooldowns = new Collection();

module.exports = async (client, msg) => {
    if (msg.author.bot || !msg.guild) return;

    let prefix = client.config.PREFIX;
    let color = client.config.COLOR;
    let args = msg.content.slice(prefix.length).trim().split(/ +/g);
    let command = args.shift().toLowerCase();

    if (msg.content.toLowerCase() === `<@${client.user.id}>` || msg.content.toLowerCase() === `<@!${client.user.id}>`) {
        msg.channel.send(`Prefix: \`sexy\`\nExample: \`sexy random\``);
    }
    if ((/^(https:)\/\/(nhentai+)\.(net)\/g\/[0-9]+\/?/).test(msg)) return require('../lib/NanaLink')(client, msg);
    if (!msg.content.startsWith(prefix.toLowerCase())) return undefined;
    if (!msg.guild.member(client.user).hasPermission("MANAGE_MESSAGES") && msg.guild.id != '599523411441483786') msg.channel.send(`**${nick}**, for ideal bot usage please, ask the admin or owner to give \`MANAGE_MESSAGES\` permission to my role`).then(msg=>msg.delete(10000));

    // cooldowns command
    let cmd = client.commands.get(command) || client.commands.get(client.aliases.get(command));
    if (!cmd) return;
    if (cmd.conf.owner && !client.config.OWNERS.includes(msg.author.id)) return;
    if (!cooldowns.has(cmd.help.name)) cooldowns.set(cmd.help.name, new Collection());

    let member = msg.member;
    let now = Date.now();
    let timeStamp = cooldowns.get(cmd.help.name) || new Collection();
    let cool = cmd.conf.cooldown || 5;
    let userCool = timeStamp.get(msg.author.id) || 0;
    let estimated = userCool + (cool * 1000) - now;

    if (userCool && estimated > 0) {
        return msg.channel.send(`**${member.user.username}**, you have to wait **${(estimated/1000).toFixed()}s** before use the same command`).then(msg => msg.delete(4000));
    }

    timeStamp.set(msg.author.id, now);
    cooldowns.set(cmd.help.name, timeStamp);
    cmd.run(client, msg, args, color);
}

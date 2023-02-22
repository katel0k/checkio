const path = require('path');

module.exports = {
	entry: {
		room: './js/room.js',
		index: './js/index.js'
	},
	mode: 'none',
	output: {
		filename: '[name].js',
	},
	module: {
		rules: [
			{
				test: /\.m?js$/,
				exclude: /(node_modules|bower_components)/,
				use: {
					loader: "babel-loader"
				}
			},
			{
				test: /\.css$/,
				use: [
					"style-loader",
					"css-loader"
				]
			},
			{
				test: /\.(png|svg|jpg|gif)$/,
				use: ["file-loader"]
			}
		]
	}
}
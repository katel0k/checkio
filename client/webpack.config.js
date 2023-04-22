const path = require('path');

module.exports = {
	// entry: {
	// 	room: './js/room.js',
	// 	index: './js/index.js'
	// },
	entry: './js/index.js',
	mode: 'none',
	output: {
		filename: '[name].js',
	},
	resolve: {
	  	extensions: ['.js', '.jsx'],
	},
	module: {
		rules: [
			{
				test: /\.m?jsx?$/,
				exclude: /(node_modules|bower_components)/,
				use: {
					loader: "babel-loader"
				}
			},
			{
				test: /\.css$|\.sass$/,
				use: [
					"style-loader",
					"css-loader",
					"sass-loader"
				]
			},
			{
				test: /\.(png|svg|jpg|gif)$/,
				use: ["file-loader"]
			}
		]
	}
}
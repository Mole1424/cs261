const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserWebpackPlugin = require("terser-webpack-plugin");


module.exports = function(_env, argv) {
  return {
    mode: "development",
    devtool: "source-map",
    entry: {
      src: "./public/src/index.tsx",
      styles: "./public/styles/index.scss"
    },
    output: {
      path: path.resolve(__dirname, "public/dist"),
      filename: "assets/js/[name].[contenthash:8].js",
      publicPath: "/",
      clean: true
    },
    resolve: {
      extensions: [".js", ".jsx", ".ts", ".tsx", ".scss", ".css"],
      modules: [
          path.resolve(__dirname, "public/src"),
          path.resolve(__dirname, "public/"),
          path.resolve(__dirname, "node_modules")
      ]
    },
    module: {
      rules: [
        {
          test: /.tsx?$/,
          use: "ts-loader",
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: [
            "style-loader",
            "css-loader"
          ]
        },
        {
          test: /\.s[ac]ss$/,
          use: [
              "style-loader",
              "css-loader",
              "sass-loader"
          ]
        },
        {
          test: /\.(png|jpe?g|svg|gif)$/,
          type: "asset/resource",
        }
      ]
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: path.resolve(__dirname, "public/index.html"),
        inject: true,
        favicon: "public/assets/I2I.png"
      })
    ],
    optimization: {
      minimizer: [
        new TerserWebpackPlugin({
          terserOptions: {
            compress: {
              comparisons: false
            },
            output: {
              comments: false
            }
          }
        }),
        new CssMinimizerPlugin(),
       ],
      splitChunks: {
        chunks: "all",
        minSize: 0,
        maxInitialRequests: 20,
        maxAsyncRequests: 20,
        cacheGroups: {
          vendors: {
            test: /[\\/]node_modules[\\/]/,
            name(module, chunks, cacheGroupKey) {
              const packageName = module.context.match(
                /[\\/]node_modules[\\/](.*?)([\\/]|$)/
              )[1];
              return `${cacheGroupKey}.${packageName.replace("@", "")}`;
            }
          },
          common: {
            minChunks: 2,
            priority: -10
          }
        }
      },
      runtimeChunk: "single"
    }
  };
};

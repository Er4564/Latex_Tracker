// Load configuration from environment or config file
const path = require('path');
const os = require('os');

const isLinux = os.platform() === 'linux';

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      
      // Linux-specific optimizations
      if (isLinux) {
        // Enhanced file watching for Linux
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          poll: config.disableHotReload ? false : 1000, // Check for changes every second
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/logs/**',
            '**/*.log',
            '**/public/**',
          ],
          aggregateTimeout: 300, // Delay before rebuilding
        };
        
        // Optimize for Linux file systems
        webpackConfig.resolve.symlinks = false;
        
        // Enable filesystem caching for faster rebuilds
        webpackConfig.cache = {
          type: 'filesystem',
          cacheDirectory: path.resolve(__dirname, '.webpack-cache'),
          buildDependencies: {
            config: [__filename],
          },
        };

        // Optimize memory usage
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          splitChunks: {
            chunks: 'all',
            cacheGroups: {
              vendor: {
                test: /[\\/]node_modules[\\/]/,
                name: 'vendors',
                chunks: 'all',
              },
            },
          },
        };

        // Linux-specific performance optimizations
        if (process.env.NODE_ENV === 'development') {
          // Reduce bundle size in development
          webpackConfig.devtool = 'eval-source-map';
        }
      }
      
      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        // Remove hot reload related plugins
        webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
          return !(plugin.constructor.name === 'HotModuleReplacementPlugin');
        });
        
        // Disable watch mode
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/, // Ignore all files
        };
      }
      
      return webpackConfig;
    },
  },
  style: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },
  // Disable TypeScript checking for faster builds on Linux
  typescript: {
    enableTypeChecking: !isLinux || process.env.NODE_ENV === 'production',
  },
  // Conditionally disable ESLint during build for faster compilation on Linux
  eslint: {
    enable: !isLinux || process.env.NODE_ENV === 'production',
  },
};
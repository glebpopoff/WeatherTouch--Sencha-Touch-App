Ext.ns('todaysweather', 'todaysweather.views');

Ext.setup({
    statusBarStyle: 'black',
    onReady: function() {
        todaysweather.App = new todaysweather.App({
            title: "WeatherTouch"
        });
    }
});

todaysweather.App = Ext.extend(Ext.TabPanel, {
    
    fullscreen: true,
    
    tabBar: {
        dock: 'bottom',
        layout: { pack: 'center' }
    },
    
    cardSwitchAnimation: false,
    
    initComponent: function() {

    	if (navigator.onLine) {
            this.items = [           	
            {
                xtype: 'weatherforecasttoday',
                iconCls: getWeatherTodayIcon(),
                title: 'Hourly',
                confTitle: this.title
            
            },
			
			{
                xtype: 'weatherforecast',
				iconMask: true,
				iconCls: 'info',
                title: '5 Day',
                confTitle: this.title
            
            },
			{
                xtype: 'weatherlocations',
                iconCls: 'search',
                title: 'Locations',
                confTitle: this.title
            
            }
            ];
        } else {
            this.on('render', function(){
                this.el.mask('No internet connection.');
            }, this);
        }
        
		todaysweather.App.superclass.initComponent.call(this);
    }
    
});

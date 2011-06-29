todaysweather.views.WeatherForecastToday = Ext.extend(Ext.Panel, {
    layout: 'card',
    
    initComponent: function() {
        
        this.list = new Ext.List({
            cls: 'timeline',
            emptyText   : '<p class="no-searches">Unable to retrieve data</p>',
			disableSelection: true,
            store: weatherForecastStore,
            plugins: [{
                ptype: 'pullrefresh'
            }],
			grouped : false,
            itemCls: 'weatheritem',
			itemTpl: Ext.XTemplate.from('hourly-list-tpl'),
			listeners: {
				itemtap: function (list, index, element, event) {}
			}
	
        });

		this.list.on('render', function(){
		            this.list.store.load();
		            this.list.el.mask('<span class="top"></span><span class="right"></span><span class="bottom"></span><span class="left"></span>', 'x-spinner', false);
		        }, this);

		todayWeatherForecastToolbar = new Ext.Panel({
            layout: 'fit',
            items: this.list,
            dockedItems: [{
                xtype: 'toolbar',
                title: defaultLocationName
            }
			
			],
            listeners: {
                activate: { fn: function(){
                    //this.list.getSelectionModel().deselectAll();
					//console.log('activate');
                    Ext.repaint();
                }, scope: this }
                
            }
        });
        
        this.items = todayWeatherForecastToolbar;
       	todaysweather.views.WeatherForecast.superclass.initComponent.call(this);
    },
    
    onSelect: function(sel, records){
        if (records[0] !== undefined) {
            
            /*var bioCard = new mytracker.views.MyTeamDetail({
                prevCard: this.listpanel,
                record: records[0]
            });
            
            this.setActiveItem(bioCard, 'slide');
            */
        }
    }
});

Ext.reg('weatherforecasttoday', todaysweather.views.WeatherForecastToday);

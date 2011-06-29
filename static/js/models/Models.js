Ext.regModel('OfflineLocation', {
	fields: [
		{name: 'location',    type: 'string'},
		{name: 'zip',    type: 'string'},
		{name: 'lat',    type: 'string'},
		{name: 'lon',    type: 'string'},
		{name: 'lookup_id', type: 'string'}
	],
	proxy: {type: 'localstorage', id: 'weatherlocationproxy'}
 });

Ext.regModel('HourlyData', {
	fields: [
			"chancePrecip",
			"dateTimeStr",
			"dateTime", 
			"desc",
			"humidity",
			"icon",
			"temperature",
			"windDir",
			"windSpeed",
			"weekDay",
			"precipChance"
			],
	belongsTo: { model: 'WeatherForecastFiveDay', name: 'weatherforecast' },
	});

Ext.regModel("WeatherForecastFiveDay", {
            fields: [
            	{name: "name", type: "string"},
            	{name: "low", type: "string"},
            	{name: "high", type: "string"},
            	{name: "pred", type: "string"},
            	{name: "imgIcon", type: "string"},
            	{name: "daydesc", type: "string"},
				{name: "hourly", type: "array" }

        	],
			hasMany: {model: 'HourlyData', name: 'hourly'},
			proxy: {type: 'localstorage', id: 'weatherforecastproxy'}
        });

var locationAjaxStore = new Ext.data.Store({
	    model: 'OfflineLocation',
	    autoLoad: true,
		noCache: true,
	    proxy: {
	        type: 'ajax',
	        method: 'get',
	        url : '/location',
	        extraParams: {},
	        reader: {
	            type: 'json',
	            root: 'results'
	        }
	    }
	});
	

	
	var weatherForecastStoreStatic = new Ext.data.Store({
		    model: 'WeatherForecastFiveDay',
		    autoLoad: true,
		    data: [
			        {name: 'CT',   low: '86', high: '95', pred: 'test', imgIcon: '206', dayDesc: 'test'},
			       {name: 'CT1',   low: '86', high: '95', pred: 'test', imgIcon: '206', dayDesc: 'test'},
					{name: 'CT2',   low: '86', high: '95', pred: 'test', imgIcon: '206', dayDesc: 'test'}
					
			    ]
		});

var weatherForecastStore = new Ext.data.Store({
	    model: 'WeatherForecastFiveDay',
	    autoLoad: true,
		getGroupString : function(record) {
			/*var hourlyArray = record.get('hourly');
			if (hourlyArray)
			{	var groupStr = ''
				for (var i = 0; i < hourlyArray.length; i++)
				{
					var obj = hourlyArray[i];
					console.log(obj.weekDay + ':' + obj.dateTimeStr);
					if (obj && obj.weekDay != '')
					{
						groupStr = obj.weekDay;
					}
				}
				return groupStr;
			}*/
			return record.get('name');
		},
	    proxy: {
	        type: 'ajax',
	        method: 'get',
	        url : '/weather?loc=' + defaultZip,
	        extraParams: {},
	        reader: {
	            type: 'json',
	            root: 'results'
	        }
	    }
	});

var gpsCoords = 
	{
		lat: '',
		lon: ''
	};

var formFields = 
		{
			zipField: new Ext.form.Text(
			{
				type: 'textfield',
				placeHolder: 'my zip',
				name : 'zip',
				label: 'ZIP',
				useClearIcon: true,
				autoCapitalize : false
		   	}),
			stateField: new Ext.form.Text(
			{
				xtype: 'textfield',
				name : 'city',
				label: 'City/State',
				placeHolder: 'City,State',
				useClearIcon: true,
				autoCapitalize : false
		   }),
		
		  locationList: new Ext.form.Select(
				{
                  	xtype: 'selectfield',
                  	name : 'saved_locations',
					id : 'saved_locations',
					valueField : 'lookup_id',
                  	displayField : 'location',
                  	store : locationAjaxStore,
						listeners: 
						{
							render: function () 
							{
								//console.log('locationList render')
							},
							change: function(selectfield, block) 
							{
                      			console.log('Reloading Data...' + selectfield.value);
								weatherForecastStore.proxy.url = '/weather?loc=' + selectfield.value;
								weatherForecastStore.load();
                  			}
						}
              		}
				)

		};
		
var todayWeatherForecastToolbar = null;
var fiveDayWeatherForecastToolbar = null;
var myLocationListPanel = null;
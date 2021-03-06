DELIMITER ;;
CREATE TRIGGER CHECK_MAX_ROW  AFTER UPDATE ON AccessPointMetric 
FOR EACH ROW 
BEGIN   
select count(*) INTO @maxvalue from AccessPointMetricLog where name=new.name;   
INSERT INTO AccessPointMetricLog(name,clients,datereg) VALUES (new.name,new.clients,new.datereg);   
IF @maxvalue = 336 THEN     
	select id INTO @iddelete from AccessPointMetricLog where name=new.name ORDER BY datereg limit 1;
        DELETE FROM AccessPointMetricLog WHERE id = @iddelete;    
END IF; 

END;;
DELIMITER ;


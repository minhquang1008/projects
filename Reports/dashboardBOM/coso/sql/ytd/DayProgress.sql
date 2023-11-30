/*MTD*/

/*Day Progress*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @LastDateOfMonth DATETIME;
SET @LastDateOfMonth = (SELECT EOMONTH(@Date));

DECLARE @At INT;
SET @At = (SELECT COUNT(*) FROM [Date] WHERE [Work] = 1 AND [Date] BETWEEN @FirstDateOfMonth AND @Date)

DECLARE @Total INT;
SET @Total = (SELECT COUNT(*) FROM [Date] WHERE [Work] = 1 AND [Date] BETWEEN @FirstDateOfMonth AND @LastDateOfMonth)

SELECT DISTINCT @At [At], @Total [Total] 
FROM [BranchTargetByYear]
WHERE [Year] = YEAR(@Date)


END

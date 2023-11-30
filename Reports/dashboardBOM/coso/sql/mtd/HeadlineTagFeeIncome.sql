/*MTD - BOM - CoSo*/

/*Headline Tag - Fee Income (Phần trăm hoàn thành chỉ tiêu tháng - Phí giao dịch)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonthOfCurrentYear DATETIME;
SET @FirstDateOfMonthOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfMonthOfPreviousYear DATETIME;
SET @FirstDateOfMonthOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),MONTH(@DateOfPreviousYear),1,0,0,0,0));

WITH 

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [PrevValuePeriod] AS (
	SELECT
		SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

, [CurrentValuePeriod] AS (
	SELECT
		SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

SELECT
	[CurrentValuePeriod].[FeeInCome] [FeeIncome]
	, [CurrentValuePeriod].[FeeInCome] - [PrevValuePeriod].[FeeInCome] [AbsoluteChange]
	, CASE 
		WHEN [PrevValuePeriod].[FeeInCome] = 0 THEN 0
		ELSE [CurrentValuePeriod].[FeeInCome] / [PrevValuePeriod].[FeeInCome] - 1
	END [RelativeChange]
FROM [PrevValuePeriod]
CROSS JOIN [CurrentValuePeriod]


END
